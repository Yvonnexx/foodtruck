foodtruck-app
=============
*Project:

 Food Trucks 

*Link to the hosted application: http://yvonnexiao.kd.io:5000/

Have hosted the app on koding, but it will ask you to click on the link on the page to redirect to the app url. It’s an default setting for kidding and I cannot change that.

*Link to the Hosted repository:
https://github.com/Yvonnexx/foodtruck

*Technical Track:

 Back-end

*Reasoning behind my technical choices:

Have some relevant experience building a back-end service for the web application.

*Level of experience with technical stack:

 Python  Advanced	
 Javascript  Beginner	
 Flask	Beginner

This app is mainly focusing on the back-end service of food trucks. 

*To Run:

$python test.py
Then type in the url http://localhost:5000
Once open the above url, you will see a marker on the google maps. You can drag the marker to different addresses and it will show the images of the food-truck nearby. You can click on the image and the information for this food truck will be shown on the web page.

$python run_test.py
This is to run the unit test modules written for this service.

*Design Decison:
It took me a while to make the decision where to store the data, whether in the cache or in a database. As for the database, I initially thought about using MongoDB to compute nearest food truck near a specific location but I decided to use cache instead for the following reasons.
First, the food-truck data is not very large, it's reasonable to save them in cache. Each time a user send a request to the server, the backend server will check if the eTag of the url data has been modified. If not, we can just compute the result using the KDTree in the cache which has been already built. Querying cache is faster than database query operations. 
Secondly, food-truck information changes frequently. Updating the database each time to check consistency would be not very fast.
Based on my understanding of the food-truck service, I think using cache is a better choice than using database.

I have also given a lot thoughts about how to compute the nearest neighbors near a specific location. The reason why I use KDTree is finding 1 nearest neighbor in a balanced k-dtree with randomly distributed points take O(log n) time on average.

*The Development

Frontend

-HTML

-CSS

-Javascript

-Google Maps API

Backend

-Flask(Python)

-Socrate Open Data API 

-scipy.spatial.kdtree (Python)

-cPickle(Python)

-flask.ext.cache (Python)

*Where I spent my Time
Time is limited for the one week code challenge since I'm still doing an internship.
I spent about two nights thinking about the structure of the back end services.
Spent two days learning all the APIs needed like flask.ext.cache.
Also spent one day learning how to add eTag using Flask cause we can check the status of the eTag, if it's 304 which means the json url Socrate Open Data API provided page has not been modified, we can just use the KDTree already cached.
Spent a day learning how to find the nearest location near a specific location. Then I chose KDTree since the query time for KDTree is just O(log N) althougth the tree construction is a little complex, but we can use cache and eTag to improve the performance.
Spent like one day writing all the tests for each function since any untested code is broken code.

*Shortcomings:
Not an expert in the front end, still a beginner in HTML, CSS, Javascript, and Google Maps API. Didn't have time to create a better look front end page.

*Link to other code:

https://github.com/Yvonnexx/whattoeat

*Linkedln profile:

https://www.linkedin.com/in/yvonnexiaoxiao

*Link to the resume

https://github.com/Yvonnexx/resume
