import numpy as np
import pandas as pd
import os
import json
import re
import base64

# import tencent ocr api
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models


def dataFromPictures(picture, SecretId, SecretKey):
    resp = None
    # try:
    with open(picture, "rb") as f:
        img_data = f.read()
    img_base64 = base64.b64encode(img_data)
    cred = credential.Credential(SecretId, SecretKey)  # Secret ID and Key
    httpProfile = HttpProfile()
    httpProfile.endpoint = "ocr.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile)

    req = models.TableOCRRequest()
    # params = '{"ImageBase64":"' + str(img_base64) + '"}'
    params = '{"ImageBase64":"' + str(img_base64, 'utf-8') + '"}'
    req.from_json_string(params)
    resp = client.TableOCR(req)
    #     print(resp.to_json_string())

    # except TencentCloudSDKException as err:
    #     print(err)

    ## load resp to json
    result1 = json.loads(resp.to_json_string())

    rowIndex = []
    colIndex = []
    content = []

    for item in result1['TextDetections']:
        rowIndex.append(item['RowTl'])
        colIndex.append(item['ColTl'])
        content.append(item['Text'])

    rowIndex = pd.Series(rowIndex)
    colIndex = pd.Series(colIndex)

    index = rowIndex.unique()
    index.sort()

    columns = colIndex.unique()
    columns.sort()

    data = pd.DataFrame(index=index, columns=columns)
    for i in range(len(rowIndex)):
        data.loc[rowIndex[i], colIndex[i]] = re.sub(" ", "", content[i])

    return result1, data


def extract_info(index_list, data):
    key_list = []
    value_list = []
    data_row, data_col = data.shape
    for i in range(data_row-1):
        for j in range(data_col-1):
            for k in index_list:
                if k == str(data.loc[i, j]):
                    key_list.append(k)
                    value_list.append(str(data.loc[i, j+1]))
    info = dict(zip(key_list, value_list))
    return info


if __name__ == '__main__':
    os.chdir("./pictures/")
    pictures = os.listdir('.')
    pic = pictures[2]
    Json_data, pandas_data = dataFromPictures(pic, "AKIDf9OM3GjdngZ4LMccT3oNq9D1lERN5SaT", "mS6VcU6RVIyNVMx2rPxGI3YnsgDSYOxH")
    print("Extraction of " + pic + " is finished.")

    index_list = ['1.合格证编号', '2.发证日期', '3.车辆制造企业名称', '4.车辆品牌/车辆名称', '5.车辆型号', '6.车辆识别号/车架号', '11.发动机号']
    info = extract_info(index_list, pandas_data)
    print(info)
