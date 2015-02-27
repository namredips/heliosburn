from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from api.models import legacy_db_model
from api.models.auth import RequireLogin
from sqlalchemy.exc import IntegrityError
import json


@csrf_exempt
def rest(request, *pargs, **kwargs):
    """
    Calls python function corresponding with HTTP METHOD name.
    Calls with incomplete arguments will return HTTP 400
    """
    if request.method == 'GET':
        rest_function = get
    elif request.method == 'POST':
        rest_function = post
    elif request.method == 'PUT':
        rest_function = put
    elif request.method == 'DELETE':
        rest_function = delete
    else:
        return JsonResponse({"error": "HTTP METHOD UNKNOWN"})

    try:
        return rest_function(request, *pargs, **kwargs)
    except TypeError:
        return HttpResponseBadRequest("argument mismatch")


@RequireLogin()
def get(request, testplan_id, rule_id=None, dbsession=None):
    """
    Retrieve rule based on testplan_id and rule_id.
    """
    if rule_id is None:
        return get_all_rules(request, testplan_id, dbsession)
    rule = dbsession.query(legacy_db_model.Rule).filter_by(id=rule_id).first()
    if rule is None:
        return HttpResponseNotFound()
    else:
        if rule.filter is not None:
            cur_filter = {
                'id': rule.filter.id,
                'method': rule.filter.method,
                'status_code': rule.filter.status_code,
                'url': rule.filter.url,
                'protocol': rule.filter.protocol,
                'ruleId': rule.filter.rule_id,
                'filterHeaders': [(h.key, h.value) for h in rule.filter.headers],
            }
        else:
            cur_filter = None

        if rule.action is not None:
            cur_action = {
                'id': rule.action.id,
                'type': rule.action.type,
                'ruleId': rule.action.rule_id,
                'actionHeaders': [(h.key, h.value) for h in rule.action.headers],
            }
        else:
            cur_action = None

        return JsonResponse({
            'id': rule.id,
            'ruleType': rule.rule_type,
            'testPlanId': rule.testplan_id,
            'filter': cur_filter,
            'action': cur_action,
            }, status=200)


def get_all_rules(request, testplan_id, dbsession=None):
    """
    Retrieve all rules for a test plan.
    """
    rules = dbsession.query(legacy_db_model.Rule).filter_by(testplan_id=int(testplan_id)).all()
    rule_list = list()
    for rule in rules:
        if rule.filter is not None:
            cur_filter = {
                'id': rule.filter.id,
                'method': rule.filter.method,
                'status': rule.filter.status,
                'url': rule.filter.url,
                'protocol': rule.filter.protocol,
                'ruleId': rule.filter.rule_id,
                'filterHeaders': [(h.key, h.value) for h in rule.filter.headers],
            }
        else:
            cur_filter = None

        if rule.action is not None:
            cur_action = {
                'id': rule.action.id,
                'type': rule.action.type,
                'rule_id': rule.action.rule_id,
                'actionHeaders': [(h.key, h.value) for h in rule.action.headers],
            }
        else:
            cur_action = None
        rule_list.append({
            'id': rule.id,
            'ruleType': rule.rule_type,
            'testPlanId': rule.testplan_id,
            'filter': cur_filter,
            'action': cur_action,
        })
    return JsonResponse({"rules": rule_list})



@RequireLogin()
def post(request, testplan_id, rule_id=None, dbsession=None):
    """
    Create new rule for testplan marked by testplan_id.
    """
    if request.method != 'POST':
        r = HttpResponse('Invalid method. Only POST method accepted.', status=405)
        r['Allow'] = 'POST'
        return r
    try:
        new = json.loads(request.body)
        assert "ruleType" in new
        assert (new['ruleType'] == "response") or (new['ruleType'] == "request")
        if "action" in new:
            assert "type" in new['action']
            assert ("response" in new['action']) or ("request" in new['action'])
            assert "headers" in new['action']
        if "filter" in new:
            assert "method" in new['filter']
            assert "statusCode" in new['filter']
            assert "url" in new['filter']
            assert "protocol" in new['filter']
            assert "headers" in new['filter']
    except ValueError:
        return HttpResponseBadRequest("invalid JSON")
    except AssertionError:
        return HttpResponseBadRequest("argument mismatch")

    rule = legacy_db_model.Rule(rule_type=new['ruleType'], testplan_id=testplan_id)
    dbsession.add(rule)

    # Handle actions
    if 'action' in new:
        rule.action = legacy_db_model.Action(type=new['action']['type'])
        dbsession.add(rule.action)

        # Action headers
        headers = list()
        for header_name, header_value in new['action']['headers']:
            headers.append(legacy_db_model.ActionHeaders(key=header_name, value=header_value))
        rule.action.headers = headers

        # Action response
        if (rule.action.type == "response") and ('response' in new['action']):
            rule.action.response = legacy_db_model.ActionResponse(
                http_protocol=new['action']['response']['http_protocol'],
                status_code=new['action']['response']['status_code'],
                status_description=new['action']['response']['status_description'],
                payload=new['action']['response']['payload']
            )
            dbsession.add(rule.action.response)

        # Action request
        if (rule.action.type == "request") and ('request' in new['action']):
            rule.action.request = legacy_db_model.ActionRequest(
                http_protocol=new['action']['request']['http_protocol'],
                method=new['action']['request']['method'],
                url=new['action']['request']['url'],
                payload=new['action']['request']['payload']
            )
            dbsession.add(rule.action.request)

    # Handle filters
    if 'filter' in new:
        rule.filter = legacy_db_model.Filter(method=new['filter']['method'], status_code=new['filter']['statusCode'],
                                      url=new['filter']['url'], protocol=new['filter']['protocol'])
        dbsession.add(rule.filter)
        headers = list()
        for header_name, header_value in new['filter']['headers']:
            headers.append(legacy_db_model.FilterHeaders(key=header_name, value=header_value))
        rule.filter.headers = headers

    #dbsession.add(rule)
    try:
        dbsession.commit()
    except IntegrityError as e:
        return HttpResponseBadRequest("constraint violated")
    r = JsonResponse({"id": rule.id})
    r['location'] = "/api/testplan/%d/rule/%d" % (testplan_id, rule.id)
    return r


@RequireLogin()
def put(request, rule_id, testplan_id=None, dbsession=None):
    """
    Update existing rule based on rule_id.
    """
    try:
        in_json = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("invalid JSON")

    rule = dbsession.query(legacy_db_model.Rule).filter_by(id=rule_id).first()
    if rule is None:
        return HttpResponseNotFound()
    else:
        if "ruleType" in in_json:
            if (in_json['ruleType'] == 'request') or (in_json['ruleType'] == 'response'):
                rule.rule_type = in_json['ruleType']
            else:
                return HttpResponseBadRequest("argument mismatch")
        if "testPlanId" in in_json:
            rule.testplan_id = int(in_json['testplan_id'])

        # Handle actions
        if "action" in in_json:
            if "type" in in_json['action']:
                rule.action.type = in_json['action']['type']
            if "headers" in in_json['action']:
                headers = list()
                for header_name, header_value in in_json['action']['headers']:
                    headers.append(legacy_db_model.ActionHeaders(key=header_name, value=header_value))
                map(dbsession.delete, rule.action.headers)
                rule.action.headers = headers

            # Action response
            if (rule.action.type == "response") and ('response' in in_json['action']):
                rule.action.response = legacy_db_model.ActionResponse(
                    id=rule.action.id,
                    http_protocol=in_json['action']['response']['http_protocol'],
                    status_code=in_json['action']['response']['status_code'],
                    status_description=in_json['action']['response']['status_description'],
                    payload=in_json['action']['response']['payload']
                )

            # Action request
            if (rule.action.type == "request") and ('request' in in_json['action']):
                rule.action.request = legacy_db_model.ActionRequest(
                    id=rule.action.id,
                    http_protocol=in_json['action']['request']['http_protocol'],
                    method=in_json['action']['request']['method'],
                    url=in_json['action']['request']['url'],
                    payload=in_json['action']['request']['payload']
                )


        # Handle filters
        if "filter" in in_json:
            if "method" in in_json['filter']:
                rule.filter.method = in_json['filter']['method']
            if "statusCode" in in_json['filter']:
                rule.filter.status_code = in_json['filter']['statusCode']
            if "url" in in_json['filter']:
                rule.filter.url = in_json['filter']['url']
            if "protocol" in in_json['filter']:
                rule.filter.protocol = in_json['filter']['protocol']
            if "headers" in in_json['filter']:
                headers = list()
                for header_name, header_value in in_json['filter']['headers']:
                    headers.append(legacy_db_model.FilterHeaders(key=header_name, value=header_value))
                map(dbsession.delete, rule.filter.headers)
                rule.filter.headers = headers
        try:
            dbsession.commit()
        except IntegrityError:
            return HttpResponseBadRequest("constraint violated")
        return HttpResponse(status=200)



@RequireLogin()
def delete(request, rule_id, testplan_id=None, dbsession=None):
    """
    Delete rule based on rule_id.
    """
    rule = dbsession.query(legacy_db_model.Rule).filter_by(id=rule_id).first()
    if rule is None:
        return HttpResponseNotFound()
    else:
        dbsession.delete(rule)
        try:
            dbsession.commit()
        except IntegrityError:
            return HttpResponseBadRequest("constraint violated")
        return HttpResponse(status=200)