import sys
import argparse
import ConfigParser
import requests
import json
import jira
import logging
import os

# Bugzilla data and JIRA fields
# In Bugzilla   In JIRA
# -----------   -------
# Product       Project
# Bug           Issue
# ID            Bugzilla ID
# Summary       Summary
# Description   Description
# Severity      Priority
# Status        Status


# Predefined Constants
ISSUE_TYPE_BUG = 'Bug'

# URLs for API requests
URL_BZ_BASE = "{}/bugzilla/rest.cgi/"
URL_BZ_TOKEN = URL_BZ_BASE + "login?login={}&password={}"
URL_BZ_BUG_DETAIL = URL_BZ_BASE + "bug?token={}&id={}"
URL_BZ_BUG_COMMENT = URL_BZ_BASE + "bug/{}/comment?token={}"
URL_BZ_PRODUCT = URL_BZ_BASE + "bug?token={}&product={}"
URL_JR_ISSUE_COMMENT = "{}/rest/api/latest/issue/{}/comment"

# Map a bugzilla product to a JIRA project:
PRODUCT_PROJECT_MAP = {
    'BZ Product 1': 'JRP1',      
    'BZ Product 2': 'JRP2',      
    'BZ Product 3': 'JRP3'
}

# Map a bug severity in Bugzilla to an issue priority in JIRA:
# Severity in Bugzilla  Priority in JIRA
# --------------------  ----------------
# Blocker               High
# Critical              High
# Major                 High
# Normal                Medium
# Minor                 Low
# Trivial               Low
# Clarification         Low
# Enhancement           Low
SEVERITY_PRIORITY_MAP = {
    'blocker': 'High',
    'critical': 'High',
    'major': 'High',
    'normal': 'Medium',
    'minor': 'Low',
    'trivial': 'Low',
    'clarification': 'Low',
    'enhancement': 'Low'
}

# Map a bug status in Bugzilla to an issue in JIRA:
# Status in Bugzilla   Status in JIRA
# ------------------   --------------
# New                   To do (Open)
# Unconfirmed           In progress
# Validation            In progress
# Assigned              In progress
# In_progress           In progress
# Reopened              To do (Open)
# Resolved              Resolved
# Verified              Done (Closed)
# Closed                Done (Closed)
BUG_STATUS_MAP = {
    'NEW': 'TO DO',
    'UNCONFIRMED': 'IN PROGRESS',
    'VALIDATION': 'IN PROGRESS',
    'ASSIGNED': 'IN PROGRESS',
    'IN_PROGRESS': 'IN PROGRESS',
    'REOPENED': 'TO DO',
    'RESOLVED': 'RESOLVED',
    'VERIFIED': 'DONE',
    'CLOSED': 'DONE'
}

# Get the bug details from Bugzilla by bug id
# arguments:    main arguments
def get_config(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', required=True)
    args = parser.parse_args(arguments)

    settings = ConfigParser.ConfigParser()
    settings.read(args.config_file)
    
    return settings

# Get the access token for Bugzilla API
# bz_server:    bugzilla server name or IP
# bz_user:      bugzilla user name
# bz_pass:      bugzilla password
def bz_get_token(
    bz_server, 
    bz_user, 
    bz_pass
):
    url_token = URL_BZ_TOKEN.format(bz_server, bz_user, bz_pass)

    # Get the access token
    response = requests.get(url_token)
    if(response.ok):
        jData = json.loads(response.content)

        return jData['token']
    else:
        print("Error returned!")

# Get the bug details from Bugzilla by bug ID or product name
# bz_server:    bugzilla server name or IP
# token:        access token for API request
# name:         product name or single bug ID
def bz_get_bug_details(
    bz_server, 
    token, 
    name
):
    if (name.isdigit()):
        bz_url = URL_BZ_BUG_DETAIL
    else:
        bz_url = URL_BZ_PRODUCT
    url = bz_url.format(bz_server, token, name)
    # print(url)

    try:
        bug_details = requests.get(url)
        if(bug_details.ok):
            jData = json.loads(bug_details.content)['bugs']

            return jData
        else:
            print("Error returned!")
    except Exception as e:
        print(e)

# Get the bug comment information from Bugzilla by bug id
# bz_server:    bugzilla server name or IP
# token:        access token for API request
# bug_id:       bug ID from bugzilla for a specific bug
def bz_get_bug_comment_by_id(
    bz_server, 
    token, 
    bug_id
):
    url = URL_BZ_BUG_COMMENT.format(bz_server, bug_id, token)
    # print(url)

    try:
        bug_comment = requests.get(url)
        if(bug_comment.ok):
            jData = json.loads(bug_comment.content)

            comments = jData['bugs'][bug_id]['comments']
            return comments
        else:
            print("Error found in bug_comment response!")
            print(bug_comment.text)
    except Exception as e:
        print(e)

# Save bugs information to a file
# name:     Bug ID or product name
# bugs:     Bugs data in json format
def save_bugs_to_file(
    name,
    bugs
):
    # Save the bugs data into a json file
    filename = 'bugzilla-data-{}.json'.format(name)
    with open(filename, 'w') as outfile:
        json.dump(bugs, outfile, indent=4, sort_keys=True)
        count = len(bugs)
        msg = ''
        if (count == 0):
            msg = "No bug is found!"
        elif (count == 1):
            msg = "-> Bug #{} is saved to file: {}".format(name, filename)
        else:
            msg = "-> {} bugs for product '{}' are saved to file: {}".format(len(bugs), name, filename)
        logging.info(msg)

# Create a jira issue with comment history
# jr_server:      jira server name or IP
# jr_user:        jira user
# jr_api_token:   jira api token
# summary:        issue summary    
# description:    issue description
# issue_type:     issue type
# priority:       issue priority
# comments:       issue comments history
def jr_create_issue_with_comments(
    jr_server, 
    jr_user, 
    jr_api_token, 
    project_key,
    bug_id,
    summary, 
    description, 
    issue_type, 
    priority,
    comments
):
    issue_dict = {
        'project': {'key': project_key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type},
        'priority': {'name': priority}
    }
    try:
        jr = jira.JIRA(jr_server, basic_auth=(jr_user, jr_api_token))
        new_issue = jr.create_issue(fields=issue_dict)
        issue_id = new_issue.id
        msg = "+ JIRA issue ({}) with issue id #{} is created for bug #{}".format(new_issue, issue_id, bug_id)
        # print(msg)
        logging.info(msg)

        for comment in comments:
            creation_time = comment.get('creation_time', '')
            creator = comment.get('creator', '')
            comment_text = comment.get('text', '')

            combined_comment = comment_text + '\nCreated by ' + creator + ' at ' + creation_time

            jr_comment = jr.add_comment(issue_id, combined_comment)

            msg = "+ Comment is added to issue id #{}".format(issue_id)
            # print(msg)
            logging.info(msg)

        msg = "+ Bug ID #{} is migrated from Bugzilla to Jira successfully with issue id #{} ({})".format(bug_id, issue_id, new_issue)
        print(msg)
        logging.info(msg)
        return issue_id
    except Exception as e:
        print(e)

# Create jira issues from bugs
# jr_server:      jira server name or IP
# jr_user:        jira user
# jr_api_token:   jira api token
# bz_server:      bugzilla server name or IP
# bz_token:       bugzilla token
# bugs:           bugs json array
# name:           product name or single bug ID
def jr_create_issues_from_bugs(
    jr_server, 
    jr_user, 
    jr_api_token, 
    jr_project_key,
    bz_server,
    bz_token,
    bugs,
    name
):
    count = 0
    jData = {}

    try:
        for bug in bugs:
            # Create the issue with basic information
            bug_id = str(bug.get('id', ''))
            print('Bug ID #{}'.format(bug_id))
            bz_desc = '''From bugzilla - Bug ID#: {}\n
                assigned_to:\n{}\nassigned_to_detail:\n{}\n
                cc:\n{}\ncc_detail:\n{}\n
                component:\n{}\ncreation_time:\n{}\n
                creator:\n{}\ncreator_detail:\n{}\n
                last_change_time:\n{}\nop_sys:\n{}\n
                qa_contact:\n{}\nqa_contact_detail:\n{}\n
                target_milestone:\n{}\nversion:\n{}\n'''

            formated_bz_desc = bz_desc.format(
                bug_id,
                bug.get('assigned_to', ''),
                bug.get('assigned_to_detail', ''),
                bug.get('cc', ''),
                bug.get('cc_detail', ''),
                bug.get('component', ''),
                bug.get('creation_time', ''),
                bug.get('creator', ''),
                bug.get('creator_detail', ''),
                bug.get('last_change_time', ''),
                bug.get('op_sys', ''),
                bug.get('qa_contact', ''),
                bug.get('qa_contact_detail', ''),
                bug.get('target_milestone', ''),
                bug.get('version', '')
            )

            # Get bug comment history from data file if it exists already
            comment_filename = 'bugzilla-data-{}-comments.json'.format(name)
            if (os.path.exists(comment_filename)):
                msg = "Bug comment history data file for {} already exists, the migration will be based on the data file directly!".format(name)
                # print(msg)
                logging.info(msg)

                with open(comment_filename) as jfile:
                    comments = json.load(jfile).get(bug_id, '')
            # Get bug comment history from bugzilla if the data file doesn't exist
            else:
                msg = "Bug comment history data file for {} does not exist, the migration will retrieve bugs information from bugzilla!".format(name)
                # print(msg)
                logging.info(msg)

                # Get the comment history of the bug
                comments = bz_get_bug_comment_by_id(bz_server, bz_token, bug_id)

            jData[bug_id] = comments
            # print(json.dumps(jData, indent=4, sort_keys=True))

            issue_id = jr_create_issue_with_comments(
                jr_server, 
                jr_user, 
                jr_api_token,
                jr_project_key,
                bug_id,
                summary = bug.get('summary', ''),
                description = formated_bz_desc,
                issue_type = ISSUE_TYPE_BUG,
                priority = SEVERITY_PRIORITY_MAP[bug.get('severity', '')],
                comments = comments
            )

            # Update the issue status as per the original bug status
            issue_status = BUG_STATUS_MAP[bug['status']]
            if (issue_status != "TO DO"):
                jr_transit_issue(
                    jr_server, 
                    jr_user, 
                    jr_api_token,
                    issue_id, 
                    transition = issue_status
                )

            count += 1
    
        # Save the bugs comment history into a json file
        comment_filename = 'bugzilla-data-{}-comments.json'.format(name)
        if (not os.path.exists(comment_filename)):
            with open(comment_filename, 'w') as outfile:
                json.dump(jData, outfile, indent=4, sort_keys=True)
            
        msg = "-> Comment history for {} is saved to file: {}".format(name, comment_filename)
        # print(msg)
        logging.info(msg)

        msg = "Total number of issues that have been migrated for {} from Bugzilla: {}".format(name, count)
        print(msg)
        logging.info(msg)

        return count
    except Exception as e:
        print(e)

# Get a JIRA issue field value
# jr_server:        jira server name or IP
# jr_user:          jira user
# jr_api_token:     jira api token
# issue_id:         issue id
# issue_field_name: issue field name 
def jr_get_issue_field(
    jr_server, 
    jr_user, 
    jr_api_token, 
    issue_id,
    issue_field_name
):
    try:
        jr = jira.JIRA(jr_server, basic_auth=(jr_user, jr_api_token))
        issue = jr.issue(issue_id)
        field_value = issue.raw['fields'][issue_field_name]

        print(field_value)
        return field_value
    except Exception as e:
        print(e)

# Check if a bug has already been migrated or not in JIRA
# jr_server:        jira server name or IP
# jr_user:          jira user
# jr_api_token:     jira api token
# issue_id:         issue id
# issue_field_name: issue field name 
# def isBugMigratedToJira(bug_id):
    

# Transit a jira issue
# jr_server:        jira server name or IP
# jr_user:          jira user
# jr_api_token:     jira api token
# issue_id:         issue id    
# transition:       target transition
def jr_transit_issue(
    jr_server, 
    jr_user, 
    jr_api_token, 
    issue_id,
    transition
):
    try:
        jr = jira.JIRA(jr_server, basic_auth=(jr_user, jr_api_token))
        trans = jr.transitions(issue_id)

        jr.transition_issue(issue_id, transition)
        msg = "-> JIRA issue {} transition performed: {}".format(issue_id, transition)
        # print(msg)
        logging.info(msg) 
    except Exception as e:
        print("Error occured while transit jira issue {} to {}".format(issue_id, transition))
        print(e)

# Get bug details (from data file or bugzilla)
def get_bug_details(
    bz_server, 
    token, 
    name
):
    # Get bug details from data file if it exists already
    filename = 'bugzilla-data-{}.json'.format(name)
    if (os.path.exists(filename)):
        msg = "Bug details data file for {} already exists, the migration will be based on the data file directly!".format(name)
        # print(msg)
        logging.info(msg)

        with open(filename) as jfile:
            bugs = json.load(jfile)

    # Get bug details from bugzilla if the data file doesn't exist
    else:
        msg = "Bug details data file for {} does not exist, the migration will retrieve bugs information from bugzilla!".format(name)
        # print(msg)
        logging.info(msg)

        # Retrieve bug details
        bugs = bz_get_bug_details(bz_server, token, name)

        # Store bugs to a file
        save_bugs_to_file(name, bugs)
    
    total = len(bugs)
    if (total <= 1):
        msg = "{} bug has been found for '{}'".format(total, name)
    else:
        msg = "{} bugs have been found for '{}'".format(total, name)
    # print(msg)
    logging.info(msg)
    return bugs

def test(
    jr_server, 
    jr_user, 
    jr_api_token
):
    # jr_get_issue_field(
    #     jr_server, 
    #     jr_user, 
    #     jr_api_token, 
    #     '27635',
    #     'description'
    # )

    jr_transit_issue(
        jr_server, 
        jr_user, 
        jr_api_token,
        '27671', 
        'RESOLVED'
    )

def main(arguments):
    try:
        settings = get_config(arguments)
        # Read the bugzilla configuration
        bz_server = settings.get('bugzilla', 'server')
        bz_user = settings.get('bugzilla', 'user')
        bz_pass = settings.get('bugzilla', 'pass')
        bz_products = settings.get('bugzilla', 'products')

        # # Retrieve the access token
        token = bz_get_token(bz_server, bz_user, bz_pass)

        # Read the jira configuration
        jr_server = settings.get('jira', 'server')
        jr_user = settings.get('jira', 'user')
        jr_api_token = settings.get('jira', 'api-token')

        log_file_name = 'bugzilla2jira.log'
        logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s', 
            filename=log_file_name,
            level=logging.INFO
        )

        names = bz_products.split(',')

        for name in names:
            # test(
            #     jr_server, 
            #     jr_user, 
            #     jr_api_token
            # )

            # Get the bug details
            bugs = get_bug_details(bz_server, token, name)

            # Create Jira issues based on the product bugs
            jr_project_key = PRODUCT_PROJECT_MAP[name]
            jr_create_issues_from_bugs(
                jr_server, 
                jr_user, 
                jr_api_token,
                jr_project_key,
                bz_server,
                token,
                bugs,
                name
            )

    except Exception as e:
        print(e)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))