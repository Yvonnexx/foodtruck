foodtruck-app
============

Project
--------
Food Trucks 

Link to the hosted application
----------
new link http://ec2-54-183-252-236.us-west-1.compute.amazonaws.com/ (in case one of them broken)
http://yvonnexiao.kd.io:5000/


Have hosted the app on koding, but it will ask you to click on the link showing on the webpage to redirect to the app . It’s a default setting for koding.

Link to the hosted repository
------------------
https://github.com/Yvonnexx/foodtruck

Technical Track
----------------
Back-end

Reasoning behind my technical choices
--------------------------------------
Have some relevant experience building a back-end service for web-app.

Level of experience with technical stack
-----------------------------------------
Python Advanced 
Javascript Beginner 
Flask Beginner

This app is a full-stack application, it provides a service that enables the users see all the food trucks around them.

To Run
-------
To run the unit tests, do:
```
$ python test.py
```

To run the app, do:
```
$ python run_test.py
```
Then go to http://localhost:5000 in the browser.

Once open the above url, you will see a marker on the google maps. You can drag the marker, once you done dragging, click on the truck icon image, you will see the information for this food truck.

Design Decision
---------------
It took me a while to make the decision about how to store the data. My initial consideration was to persist all data in the database. I did some research on different databases and narrowed down to MongoDB and PostgreSQL, because they both support geographical data query, which makes problems like k nearest neighbors trivial. However, considering that the data set is relatively small, it is reasonable to save them in cache, and only call the SODA api when needed(cache miss or etag mismatch).

Having the storage solution concluded, the next challenge would be to compute k nearest neighbors. A little Google search brought me to an awesome Python library, scipy. Scipy provides a data structure called KD-Tree, which computes k nearest neighbors in O(log N) time complexity. I decided to build the tree right after the SODA api call and store the pickled tree in cache, so I can always have the most up to date data, and have the ability to compute the results lightning fast.

Even though I used cache at this time, that does not mean I will not use database in the future. In following development, I will setup a database and periodically persist data from cache.

The Development
---------------

**Frontend**
* HTML
* CSS
* Javascript
* Google Maps API

**Backend**
* Python
* Flask
* Socrate Open Data API
* scipy

Where I spent my Time
---------------------
Time is limited for the one week code challenge since I'm still doing an internship. I spent about two nights thinking about the architecture of the services. Spent two days learning all the tools needed like flask. Spent a day learning how to find the k nearest location. Then I chose KD-Tree since its query time complexity is only O(log N). Although the tree construction is a little complex, I can use cache and eTag to greatly improve the performance. Most of the other times are spent on coding and testing, I believe that any untested code is broken code.

Shortcomings
-------------
Not an expert in the front end, still a beginner in HTML, CSS, Javascript, and Google Maps API. 

Didn't have time to create a better look front end page.

**Link to other code**
https://github.com/Yvonnexx/whattoeat

**Linkedln profile**
https://www.linkedin.com/in/yvonnexiaoxiao

**Link to the resume**
https://github.com/Yvonnexx/resume
