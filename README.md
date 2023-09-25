# Python tourism scrapper

## About
This Python script scraps a website to extract data about different city tours related to the tourism industry. It outputs the data in JSON format, which can be used to create a database, generate a website, or analyse the data.

## Features
* Extracts data for different excursions and tours.
* Outputs the data in JSON format.

## Output example
```
JSON
{
  "info": {
    "type": "sightseeing",
    "title": "New York City Sightseeing Tour",
    "description": "This tour will take you to all of the most popular tourist attractions in New York City, including the Empire State Building, the Statue of Liberty, and Times Square.",
    "duration": "2 hours"
  },
  "path": [
    {
      "latitude": 40.7127837,
      "longitude": -74.0059413
    },
    {
      "latitude": 40.712841,
      "longitude": -74.004446
    },
    {
      "latitude": 40.712398,
      "longitude": -74.005725
    }
  ],
  "spots": [
    {
      "name": "Empire State Building",
      "latitude": 40.7484404,
      "longitude": -73.9856644,
      "img": "https://example.com/images/empire-state-building.jpg",
      "description": "The Empire State Building is a 102-story Art Deco skyscraper in Midtown Manhattan, New York City, and is one of the most iconic buildings in the world."
    },
    {
      "name": "Statue of Liberty",
      "latitude": 40.689231,
      "longitude": -74.044444,
      "img": "https://example.com/images/statue-of-liberty.jpg",
      "description": "The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York Harbor in New York City, in the United States. The copper statue, a gift from the people of France to the people of the United States, was designed by French sculptor Frédéric Auguste Bartholdi and its metal framework was built by Gustave Eiffel. The statue was dedicated on October 28, 1886."
    }
  ]
}
```
## Update
This script serves as a demonstration of its functionality and is not meant for practical data extraction purposes. To protect the website's business model and data, please be aware that the URL hardcoded within this script is fictional.
