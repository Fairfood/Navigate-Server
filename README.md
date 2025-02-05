
**Navigate Documentation**


## Overview

Navigate is an MVP platform designed to monitor key areas like deforestation 
and living income. Users can switch between these categories to track and 
analyze data for each. The platform provides insights and tools to help 
manage and address environmental, economic, and social challenges effectively.

**This is just an MVP and not developed for production use. There are a**
**lot of areas in which we can improve, which need to be scoped out in detail.**


### Map

The satellite map report feature enables users to track value ranges across 
different regions using visual indicators like colors or symbols. It helps 
to highlight variations in data, making it easier to identify patterns and 
trends on the map. This tool offers a clear and intuitive way to analyze 
geographic data for better decision-making.

### Assessment section

The assessment section within each pillar delivers the evaluation values, 
offering a detailed insight into the performance or status of each component. 
This section helps users understand specific metrics and their implications 
for comprehensive analysis.

### Deforestation assessment

This section offers a deforestation assessment based on data analysis of 
multiple areas using satellite imagery. It evaluates key factors such as 
tree cover extent and primary forest loss. The impact matrix highlights 
non-acceptable outcomes across several indicators, including total tree 
area lost, deforestation event frequency, and share, indicating critical 
environmental issues in the analyzed regions.

### Living income assessment

This section provides a living income assessment, focusing on the 
socio-economic conditions of a country with a significant agricultural 
workforce. It highlights the gap between current payments and the required 
living income price for agricultural production. The analysis shows a 
substantial price gap, indicating that workers are being paid less than 
what is necessary to achieve a sustainable living income.

### Summary section

The summary section consolidates key evaluation values from each pillar, 
providing an overview of overall performance. It highlights critical 
metrics and their implications, offering a concise and comprehensive 
snapshot for effective analysis and decision-making.

### Deforestation Summary

This section provides an overview of how to assess deforestation risks. 
It follows specific standards such as the EU Deforestation Regulation (EUDR) 
and Rainforest Alliance guidelines. Measures tree cover loss within a 
113-meter radius around farms and monitors protected areas within a 2-kilometer 
proximity. Key indicators include the total area of tree cover loss, the 
number of events leading to deforestation, and losses in protected areas. 
These assessments help identify the impact across various certification schemes 
like Rainforest Alliance, Fairtrade, and EUDR.

### Living income assessment

This section presents a demographic and agricultural overview of Honduras. 
It highlights the country’s population distribution, with a significant 
portion engaged in agriculture, which contributes notably to the GDP. Key 
metrics include the number of agricultural cooperatives, the total and average 
farm plot sizes, and the gender distribution of farmers. It also reviews 
essential financial indicators like living income prices, production costs, 
and yield rates. Farmers are categorized based on economic performance, with 
groups defined by income, production costs, and productivity levels.

### Intervention sections

To improve farmers’ outcomes, suggested interventions include training in 
sustainable farming practices, access to better seeds and tools, and 
enhanced irrigation techniques. Supporting cooperative structures can boost 
bargaining power, while providing financial literacy programs and microloans
will empower farmers economically. Additionally, promoting agroforestry and 
crop diversification can enhance resilience to climate change and market 
fluctuations.


## Supported Features and best practices

* Users can select impact areas on a map by adjusting filters for supply chain, 
  country, and batch.
* This allows flexibility in viewing impacts across different segments of the 
  value chain.
* In the Living Income category, users can choose to display values as either 
  the mean or median.
* This feature enables more tailored and precise data analysis.


## How Do We Calculate Deforestation

The ForestAnalyzer class is a wrapper designed to perform forest-related 
analyses using Google Earth Engine (EE) data. it is located in 
`v1/farms/earth_engine.py`. It calculates key statistics 
for farm properties, including tree cover, primary forest area, protected 
areas, and yearly tree cover loss. The analysis is based on geoJSON input 
representing farm locations (either Point or Polygon). You can find 
the data souces we are using in the file.

Key features of the ForestAnalyzer include:
* Tree Cover Analysis: Measures the tree cover area within the farm's polygon, 
  considering a specified canopy density.
* Primary Forest Area: Calculates the area of primary forest within the 
  farm boundary.
* Protected Areas: Determines the total protected area within the farm's 
  boundary.
* Yearly Tree Cover Loss: Tracks tree cover loss over time, segmented by 
  different canopy density thresholds.

The class integrates with sustainability standards like Rainforest Alliance, 
Fairtrade, and EUDR, each with distinct canopy density thresholds 
(10% for Rainforest Alliance and Fairtrade, 30% for EUDR) and different 
timeframes for analyzing tree cover loss. The analysis helps in assessing 
environmental impacts based on these standards.

The class uses Earth Engine for spatial analyses, and handles common 
geospatial data issues like incorrect or malformed polygons.


### Standards for Analysis

*Rainforest Alliance*
* Canopy Density: 10%
* Tree Cover Loss Year: Greater than 2014.

*Fairtrade*
* Canopy Density: 10%
* Tree Cover Loss Year: Greater than 2019.

*EUDR* (EU Deforestation Regulation)
* Canopy Density: 30%
* Tree Cover Loss Year: Greater than 2020.


### Key Attributes:

* polygon: The target geographic area for analysis, defined as a polygon.
* buffer_area: Optional buffer area around the polygon for extended analysis.
* canopy_dens: A canopy density threshold for identifying tree cover.
* dataset_tree_cover: Earth Engine dataset for global tree cover change.
* dataset_primary_forest: Earth Engine dataset for primary humid tropical 
  forests.
* dataset_protected_areas: Earth Engine dataset for protected areas.


### Key Features

* Canopy Density Thresholds:
    * Rainforest Alliance & Fairtrade: Canopy density threshold of 10%.
    * EUDR: Canopy density threshold of 30%.
* Yearly Tree Cover Loss: Tree cover loss is calculated for each year based on 
  different standards:
    * Rainforest Alliance: Year greater than 2014.
    * Fairtrade: Year greater than 2019.
    * EUDR: Year greater than 2020.


## Installation

1. Clone the repository:

  ```
  git clone git@git.cied.in:fairfood/trace-v2/backend/navigate.git .
  ```

2. Navigate to the project directory:

  ```
  cd your-project
  ```

3. Create a virtual environment:

  ```
  python -m venv venv
  ```

4. Activate the virtual environment:

  * On Windows: ```venv\Scripts\activate``
  * On Unix or MacOS: ```source venv/bin/activate```

5. Install dependencies:

  ```
  pip install -r requirements/local.ext
  ```


## Configuration

1. Create a .env file in the project root and configure environment variables:

  ```env
  [app]
  ENVIRONMENT=***********************
  DEPLOYMENT=***********************
  ROOT_URL=***********************
  FRONTEND_ROOT_URL=***********************

  [django]
  SECRET_KEY=***********************
  HASHID_SALT=***********************


  [database]
  DB_NAME=***********************
  DB_USER=***********************
  DB_PASSWORD=***********************
  DB_HOST=***********************
  DB_PORT=***********************
  REDIS_URL=redis://localhost
  REDIS_PORT=6379

  [email]
  EMAIL_HOST=***********************
  EMAIL_HOST_USER=***********************
  EMAIL_HOST_PASSWORD=<***********************

  [lib]
  # need to be changed for trace_connect
  AWS_ACCESS_KEY_ID=***********************
  AWS_SECRET_ACCESS_KEY=***********************
  AWS_STORAGE_BUCKET_NAME=***********************
  TOTP_SECRET=***********************
  SENTRY_DSN=***********************
  TRACE_OAUTH2_CLIENT_ID = ***********************
  EE_SERVICE_ACCOUNT = ***********************
  EE_SERVICE_ACCOUNT_CREDENTIAL_PATH = ***********************
  ```

2. Apply migrations:

  ```bash
  python manage.py migrate
  ```


## Database Setup

1. Create a super user with email as username and password.

  ```
  python manage.py createsuperuser
  ```


## Usage

For running server locally

Access the Django admin interface by navigating to 
[Navigate Django Admin](https://navigate.api.fairfood.org/navigate/admin/) 
and log in with the superuser credentials created earlier.


## API Endpoints

* Open your browser and go to {root_url}/navigate to view the available API 
  endpoints.
* Use tools like [curl](https://curl.se/) or [Postman](https://www.postman.com/) 
  to make HTTP requests to the API endpoints.


## Testing

* To run tests for the Django DRF project, use the following command:

```
python manage.py test
```

* Running Specific Tests

  ```
  python manage.py test <app_name>.tests.test_module
  ```

## Coverage

* Then run the tests with coverage:
  ```
  coverage run manage.py test
  ```

* And generate a coverage report:
  ```
  coverage report -m
  ```

## Contributing

We welcome contributions from the community! If you would like to contribute to 
this Django DRF project, please follow the guidelines below:


### Issues

* Before submitting a new issue, please check the [issue tracker]
(https://github.com/your-username/your-project/issues) to see if the issue has 
already been reported or discussed.
* When creating a new issue, provide a clear and detailed description, 
  including steps to reproduce if applicable.
* If you're reporting a bug, include information about your environment 
  (Django and DRF versions, database, operating system, etc.).


### Pull Requests

1. Fork the repository:

  ```
  git clone https://github.com/your-username/your-project.git
  cd your-project
  git fork
  ```

2. Create a new branch:

  ```
  git checkout -b feature-branch
  ```

3. Make your changes and commit:

  ```
  git add .
  git commit -m "Your descriptive commit message"
  ```

4. Push to the branch:

  ```
  git push origin feature-branch
  ```

5. Submit a pull request:
    * Go to the [Pull Requests]
      (https://github.com/your-username/your-project/pulls) tab in the 
      repository.
    * Click on "New Pull Request" and select the branch you just pushed.

6. Follow the pull request template and provide necessary details.


## Coding Standards

* Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide 
  for Python code.
* Write meaningful commit messages and keep the commit history clean.


## Testing

* Ensure that your changes do not break existing tests.
* If you're adding a new feature, include relevant tests.
* Run the test suite locally before submitting a pull request.


## Code of Conduct

Please note that this project follows the [Contributor Covenant Code of Conduct]
(https://github.com/Fairfood/). 
By participating, you are expected to uphold this code. Report any unacceptable 
behavior to [sudeesh@fairfood.org]


## Review Process

* The project maintainers will review your pull request and may provide 
  feedback or request changes.
* Once the changes are approved, the pull request will be merged.


## Contact Information

If you have any questions, suggestions, or feedback, feel free to reach out:
* Email: [sudeesh@fairfood.org]

You can also open an issue on the [issue tracker]
(https://github.com/your-username/your-project/issues) for bug reports, 
feature requests, or general discussions related to the project.


We appreciate your interest and contributions to our Django DRF project!
