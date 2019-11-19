# bugzilla2jira

Import bugzilla bugs in JIRA

Simply script to read bugs from Bugzilla and create the corresponding issues in
JIRA, so you can have both tools synced.

The tool is customized to our environment where we need to do http basic auth
against the bugzilla API endpoint and we use a label in JIRA to match the
product in Buzilla. 

It uses a config file to specify the following parameters:

* Bugzilla url, user, password and product.

* JIRA url, user, password, project and product. The product is a label in JIRA.

All the bugs details and bug comment history will be saved to json files.

### Example

```
python bz2jira.py -c config

Bug ID #52090
+ Bug ID #52090 is migrated from Bugzilla to Jira successfully with issue id #35343 (JRP1-1)
Bug ID #52091
+ Bug ID #52091 is migrated from Bugzilla to Jira successfully with issue id #35344 (JRP1-2)
Bug ID #52093
+ Bug ID #52093 is migrated from Bugzilla to Jira successfully with issue id #35345 (JRP1-3)
Total number of issues that have been migrated for BZ Product 1 from Bugzilla: 3
```

The logging file will have more details: 
2019-11-17 18:42:55,251 INFO: 3 bugs have been found for 'BZ Product 1' 
2019-11-17 18:42:55,251 INFO: Bug comment history data file for BZ Product 1 does not exist, the migration will retrieve bugs information from bugzilla! 
2019-11-17 18:42:59,241 INFO: + JIRA issue (JRP1-1) with issue id #35343 is created for bug #52090 
2019-11-17 18:42:59,474 INFO: + Comment is added to issue id #35343 
2019-11-17 18:42:59,719 INFO: + Comment is added to issue id #35343 
2019-11-17 18:42:59,887 INFO: + Comment is added to issue id #35343 
2019-11-17 18:43:00,109 INFO: + Comment is added to issue id #35343 
2019-11-17 18:43:00,109 INFO: + Bug ID #52090 is migrated from Bugzilla to Jira successfully with issue id #35343 (JRP1-1) 
2019-11-17 18:43:01,212 INFO: -> JIRA issue 35343 transition performed: DONE 
2019-11-17 18:43:01,215 INFO: Bug comment history data file for BZ Product 1 does not exist, the migration will retrieve bugs information from bugzilla! 
2019-11-17 18:43:04,991 INFO: + JIRA issue (JRP1-2) with issue id #35344 is created for bug #52091 
2019-11-17 18:43:05,145 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:05,320 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:05,483 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:05,653 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:05,800 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:05,964 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:06,202 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:06,354 INFO: + Comment is added to issue id #35344 
2019-11-17 18:43:06,354 INFO: + Bug ID #52091 is migrated from Bugzilla to Jira successfully with issue id #35344 (JRP1-2) 
2019-11-17 18:43:07,240 INFO: -> JIRA issue 35344 transition performed: DONE 
2019-11-17 18:43:07,243 INFO: Bug comment history data file for BZ Product 1 does not exist, the migration will retrieve bugs information from bugzilla! 
2019-11-17 18:43:11,154 INFO: + JIRA issue (JRP1-3) with issue id #35345 is created for bug #52093 
2019-11-17 18:43:11,352 INFO: + Comment is added to issue id #35345 
2019-11-17 18:43:11,512 INFO: + Comment is added to issue id #35345 
2019-11-17 18:43:11,657 INFO: + Comment is added to issue id #35345 
2019-11-17 18:43:11,657 INFO: + Bug ID #52093 is migrated from Bugzilla to Jira successfully with issue id #35345 (JRP1-3) 
2019-11-17 18:43:12,472 INFO: -> JIRA issue 35345 transition performed: DONE 
2019-11-17 18:43:12,476 INFO: Bug comment history data file for BZ Product 1 does not exist, the migration will retrieve bugs information from bugzilla!
