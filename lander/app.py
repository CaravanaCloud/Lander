import json
import os
import boto3

ddb = boto3.client('dynamodb')


def lambda_handler(event, context):
    res_headers = {
        "Content-Type": "text/html; charset=UTF-8"
    }
    html = """<html></html>"""
    path_params = event["pathParameters"] or ""
    if isinstance(path_params,dict):
        proxy_param = path_params.get("proxy")
        if proxy_param:
            path_params= proxy_param
    path_params = "/{}".format(path_params)
    req_headers = event["headers"]
    host = "."
    if req_headers:
        host = req_headers["Host"]
        host = host.split(".")[0]
    tbl_redirects = os.environ['TBL_REDIRECTS']
    response = ddb.get_item(
        TableName=tbl_redirects,
        Key={
            'host': {
                'S': host
            },
            'path': {
                'S': path_params
            }
        }
    )
    item = response.get("Item")
    if item:
        target = item.get("target")
        target = target.get("S")
        html = """<head> 
          <meta http-equiv="Refresh" content="0; URL={}">
        </head>
        """.format(target)
        status_code = 302
        res_headers["Location"] = target
    else:
        status_code = 404

    exec_data = {
        "y-res-headers": res_headers,
        "y-statusCode": status_code,
        "y-html": html,
        "x-host": host,
        "x-path": path_params,
        "x-req-headers": req_headers,
        "k-tbl_redirects": tbl_redirects,
        "y-response": response
    }
    print(json.dumps(exec_data))
    result = {
        "statusCode": status_code,
        "headers": res_headers,
        "body": html
    }
    return result
