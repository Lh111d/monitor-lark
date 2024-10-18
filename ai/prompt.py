filter_subscribers_prompt = """输入的subscription information的格式为一个list列表，格式为：
                    [[receive_id,subscription_type,subscription_content],receive_id(str)为一个用户id，subscription_type(str)为订阅类型,subscription_content(str)为订阅内容
                    [receive_id,subscription_type,subscription_content]],receive_id(str)为一个用户id，subscription_type(str)为订阅类型,subscription_content(str)为订阅内容
                    这个列表包含了所有用户的订阅信息.
                    输入的news content是我提供的一个外部信息。
                    你的任务是判断news content和哪个用户的subscription_type(订阅类型)相关。
                    注意:相关程度需要很高，如果不相关或者相关程度低则跳过。
                    最终返回给我所有相关用户（相关程度很高）的receive_id的列表，返回结果是一个list,不需要多余的描述，如果都不相关，则返回'[]'
                    格式为[['receive_id',subscription_type,subscription_content],[receive_id,subscription_type,subscription_content]....]
                    注意保持receive_id,subscription_type,subscription_content三个变量的格式不变.
                    """


ai_summary_prompt= """根据你的任务,分析我提供的信息information，
                              首先，分析我的任务，这个任务如果是提取相关信息，那么你只需要进行提取即可，不需要做任何改动，总览全文进行提取。
                              如果是分析某方面的细节，那么你需要加入自己的总结和思考。
                              其他的任务，你按照你的思路进行即可。
                              然后，你遵循一种结构化的分析总结方法，总览全文开始，然后深入到具体的细节，明确任务。
                              最后，按照任务要求实现，返回一份报告即可
                              注意:报告涉及到的###标题或####标题或##标题,都需要将其改成**包裹**
                            """