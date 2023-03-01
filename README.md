1. Clone the repository containing the Dockerfile and Docker Compose file to your local machine.

2. Open a terminal and navigate to the root directory of the cloned repository.

3. Build the Docker images by running the following command:

    `docker-compose build`

4. Once the build is complete, start the containers by running:

    `docker-compose up`

5. The MySQL database and Airflow webserver should now be running in their respective containers. You can access the Airflow web interface by navigating to http://localhost:8080 in your web browser.


6. This API provides endpoints for analyzing product pricing data.

    Endpoints

    /analysis/main_category: Returns the main category analysis of the product pricing data
    /analysis/sub_category: Returns the sub category analysis of the product pricing data
    /analysis/price: Returns the price analysis of the product pricing data
    /analysis/rating: Returns the rating analysis of the product pricing data
    /analysis/rate_count: Returns the Count of how many users rated this product


    Swagger

    Swagger documentation for this API can be found at: http://localhost:5000/swagger/

7. To stop the containers, use the following command:

    `docker-compose down`
