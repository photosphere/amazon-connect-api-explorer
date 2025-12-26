import os
import streamlit as st
import boto3
import json
import pandas as pd


# 初始化页面配置
st.set_page_config(
    page_title="Amazon Connect API Testing Tool",
    layout="wide"
)

# 页面标题
st.header("Amazon Connect API Testing Tool")

# 初始化AWS客户端


@st.cache_resource
def get_aws_client(service_name):
    return boto3.client(service_name)


# 定义API参数映射
api_params = {
    "DescribeContact": {
        "service": "connect",
        "params": ["InstanceId", "ContactId"]
    },
    "DescribeEvaluationForm": {
        "service": "connect",
        "params": ["InstanceId", "EvaluationFormId", "EvaluationFormVersion"]
    },
    "DescribeInstanceAttribute": {
        "service": "connect",
        "params": ["InstanceId", "AttributeType"]
    },
    "DescribeView": {
        "service": "connect",
        "params": ["InstanceId", "ViewId"]
    },
    "UpdateRoutingProfileDefaultOutboundQueue": {
        "service": "connect",
        "params": ["InstanceId", "RoutingProfileId", "DefaultOutboundQueueId"]
    },
    "ListInstances": {
        "service": "connect",
        "params": ["MaxResults", "NextToken"]
    },
    "ListProfileObjects": {
        "service": "customer-profiles",
        "params": ["DomainName", "ObjectTypeName", "ProfileId", "MaxResults"]
    },
    "SearchProfiles": {
        "service": "customer-profiles",
        "params": ["DomainName", "KeyName", "Values", "MaxResults"]
    }
}

# 创建服务选择下拉框
service_options = ["Amazon Connect Service",
                   "Amazon Connect Customer Profiles"]
selected_service = st.selectbox("选择服务", service_options)

# 根据所选服务显示不同的API
if selected_service == "Amazon Connect Service":
    selected_api = st.selectbox("选择API", [
                                "DescribeContact", "DescribeEvaluationForm", "DescribeInstanceAttribute", "DescribeView", "UpdateRoutingProfileDefaultOutboundQueue", "ListInstances"])
elif selected_service == "Amazon Connect Customer Profiles":
    selected_api = st.selectbox(
        "选择API", ["ListProfileObjects", "SearchProfiles"])

# 显示API参数输入框
st.subheader(f"{selected_api} 参数")

param_values = {}
if selected_api in api_params:
    for param in api_params[selected_api]["params"]:
        # 为不同参数提供默认值或说明
        help_text = ""
        default_value = ""

        if param == "MaxResults":
            default_value = "10"
            help_text = "要返回的最大结果数量"
        elif param == "NextToken":
            help_text = "用于分页的令牌"
        elif param == "InstanceId":
            help_text = "Amazon Connect 实例 ID"
        elif param == "ContactId":
            help_text = "联系人 ID"
        elif param == "EvaluationFormId":
            help_text = "评估表单 ID"
        elif param == "EvaluationFormVersion":
            help_text = "评估表单版本号（可选，留空获取最新版本）"
        elif param == "ViewId":
            help_text = "视图 ID"
        elif param == "DomainName":
            help_text = "客户资料域名"
        elif param == "ObjectTypeName":
            help_text = "资料对象类型名称"
        elif param == "ProfileId":
            help_text = "联系人资料 ID"
        elif param == "KeyName":
            help_text = "要搜索的键名"
        elif param == "Values":
            help_text = "要搜索的值（多个值用逗号分隔）"
        elif param == "RoutingProfileId":
            help_text = "路由配置文件 ID"
        elif param == "DefaultOutboundQueueId":
            help_text = "默认出站队列 ID"

        # AttributeType 使用下拉单选框
        if param == "AttributeType":
            attribute_types = [
                "INBOUND_CALLS",
                "OUTBOUND_CALLS",
                "CONTACTFLOW_LOGS",
                "CONTACT_LENS",
                "AUTO_RESOLVE_BEST_VOICES",
                "USE_CUSTOM_TTS_VOICES",
                "EARLY_MEDIA",
                "MULTI_PARTY_CONFERENCE",
                "HIGH_VOLUME_OUTBOUND",
                "ENHANCED_CONTACT_MONITORING",
                "ENHANCED_CHAT_MONITORING",
                "MULTI_PARTY_CHAT_CONFERENCE",
                "MESSAGE_STREAMING"
            ]
            param_values[param] = st.selectbox(
                f"{param}",
                options=attribute_types,
                help="实例属性类型"
            )
        else:
            param_values[param] = st.text_input(
                f"{param}", value=default_value, help=help_text)

# 运行按钮
if st.button("运行"):
    try:
        with st.spinner("正在执行API请求..."):
            # 根据选择的服务和API执行相应的调用
            if selected_api == "DescribeContact":
                client = get_aws_client("connect")
                response = client.describe_contact(
                    InstanceId=param_values["InstanceId"],
                    ContactId=param_values["ContactId"]
                )

            elif selected_api == "DescribeEvaluationForm":
                client = get_aws_client("connect")
                # 处理可选参数 EvaluationFormVersion
                api_args = {
                    "InstanceId": param_values["InstanceId"],
                    "EvaluationFormId": param_values["EvaluationFormId"]
                }
                
                if param_values["EvaluationFormVersion"]:
                    api_args["EvaluationFormVersion"] = int(param_values["EvaluationFormVersion"])
                
                response = client.describe_evaluation_form(**api_args)

            elif selected_api == "DescribeInstanceAttribute":
                client = get_aws_client("connect")
                response = client.describe_instance_attribute(
                    InstanceId=param_values["InstanceId"],
                    AttributeType=param_values["AttributeType"]
                )

            elif selected_api == "DescribeView":
                client = get_aws_client("connect")
                response = client.describe_view(
                    InstanceId=param_values["InstanceId"],
                    ViewId=param_values["ViewId"]
                )

            elif selected_api == "ListProfileObjects":
                client = get_aws_client("customer-profiles")
                # 处理可选参数
                api_args = {
                    "DomainName": param_values["DomainName"],
                    "ObjectTypeName": param_values["ObjectTypeName"],
                    "ProfileId": param_values["ProfileId"],
                }

                if param_values["MaxResults"]:
                    api_args["MaxResults"] = int(param_values["MaxResults"])

                response = client.list_profile_objects(**api_args)

            elif selected_api == "UpdateRoutingProfileDefaultOutboundQueue":
                client = get_aws_client("connect")
                response = client.update_routing_profile_default_outbound_queue(
                    InstanceId=param_values["InstanceId"],
                    RoutingProfileId=param_values["RoutingProfileId"],
                    DefaultOutboundQueueId=param_values["DefaultOutboundQueueId"]
                )

            elif selected_api == "ListInstances":
                client = get_aws_client("connect")
                # 处理可选参数
                api_args = {}

                if param_values["MaxResults"]:
                    api_args["MaxResults"] = int(param_values["MaxResults"])
                if param_values["NextToken"]:
                    api_args["NextToken"] = param_values["NextToken"]

                response = client.list_instances(**api_args)

            elif selected_api == "SearchProfiles":
                client = get_aws_client("customer-profiles")
                # 处理可选参数
                api_args = {
                    "DomainName": param_values["DomainName"],
                    "KeyName": param_values["KeyName"],
                    "Values": param_values["Values"].split(","),
                }

                if param_values["MaxResults"]:
                    api_args["MaxResults"] = int(param_values["MaxResults"])

                response = client.search_profiles(**api_args)

            # 显示结果
            st.subheader("API 响应结果")

            # 尝试将结果格式化为JSON
            st.json(response)

            # 如果结果中包含项目列表，也可以显示为表格
            if selected_api == "ListProfileObjects" and "Items" in response and response["Items"]:
                st.subheader("结果表格视图")
                df = pd.DataFrame(response["Items"])
                st.dataframe(df)

            elif selected_api == "SearchProfiles" and "Items" in response and response["Items"]:
                st.subheader("结果表格视图")
                df = pd.DataFrame(response["Items"])
                st.dataframe(df)

            elif selected_api == "ListInstances" and "InstanceSummaryList" in response and response["InstanceSummaryList"]:
                st.subheader("结果表格视图")
                df = pd.DataFrame(response["InstanceSummaryList"])
                st.dataframe(df)

    except Exception as e:
        st.error(f"执行API时出错: {str(e)}")
        st.error("请检查您的参数和AWS凭证是否正确")

# 添加关于AWS凭证的说明
st.sidebar.header("关于AWS凭证")
st.sidebar.info(
    """
    此应用程序使用boto3自动发现AWS凭证。请确保您已经配置了以下任一方式:
    1. AWS CLI (`aws configure`)
    2. 环境变量 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    3. IAM角色 (如在EC2或Lambda上运行时)
    
    确保您的凭证有足够的权限调用所选API。
    """
)
