import time
import os


from tools.rca_api_tool import call_rca_api
from tools.policy_db_tool import query_policy_db
from tools.policy_xml_tool import read_policy_xml
from tools.rca_faiss_tool import rca_doc_search
from llms.coforgeAIGardenLLM import CoforgeAIGardenLLM

llm = CoforgeAIGardenLLM()
INTERVAL = 15 * 60
XML_FOLDER = "C:/policies/generated"


#Scheduler

def scheduler():
    print("Scheduler running")
    return call_rca_api.invoke("list_failed")



# RAG Retrive Error code and use rag to fix it

def run_rca_llm(policy):
    error_code = policy["errorCode"]
    print(f"RCA LLM analysing {policy['policyName']}")

    rca_knowledge = rca_doc_search.invoke(f"{error_code} fix")

    prompt = f"""
Policy: {policy}
RCA Knowledge: {rca_knowledge}

Explain root cause and propose SQL fix.
Output ONLY SQL or NO_AUTO_FIX.
    """

    return llm.invoke(prompt).strip()



#Review Bot – Safety gate

def review_fix(sql):
    print(" Review bot checking safety")

    forbidden = ["delete", "drop", "truncate"]
    sql_l = sql.lower()

    if sql == "NO_AUTO_FIX":
        return False

    if any(word in sql_l for word in forbidden):
        return False

    if not sql_l.startswith("update"):
        return False

    return True



#  Tool Execution
def execute_fix(policy, sql):
    print("Executing fix")

    # filesystem tool
    os.makedirs(XML_FOLDER, exist_ok=True)

    # SQL tool
    query_policy_db.invoke(sql)

    # enforce exit for infra issue
    if policy["errorCode"] == "PG-FS-003":
        query_policy_db.invoke(f"""
        UPDATE policies
        SET policy_status='READY_FOR_NEXT_STAGE'
        WHERE policy_name='{policy['policyName']}'
        """)



# Verification

def verify_result(policy_name):
    result = query_policy_db.invoke(f"""
    SELECT policy_status, error_code
    FROM policies
    WHERE policy_name='{policy_name}'
    """)
    print("Verification:", result)
    return result



# Main Loop

def run():
    print("RCA agent started")

    while True:
        policies = scheduler()

        for policy in policies:
            print(f"==>> Processing {policy['policyName']}")

            sql = run_rca_llm(policy)

            if not review_fix(sql):
                print("Fix rejected by review bot")
                continue

            execute_fix(policy, sql)
            verify_result(policy["policyName"])
        time.sleep(INTERVAL)


if __name__ == "__main__":
    run()
