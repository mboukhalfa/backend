# MIRA! Project

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

Activate virtual envirement development env running


```
pipenv shell
```

Install prerequisites

```
pipenv install
```


## Deployment

Run celery worker


```
celery -A mirai_project worker -l info
```

## Shutdown

Shutdown celery worker


```
celery -A mirai_project control shutdown
```

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [ROME](https://www.django-rest-framework.org/) - Used to generate REST API
* [Pipenv](https://pipenv.readthedocs.io/en/latest/) - Dependency Management


## Authors
* **Rami Akrem Addad** - *Initial work* - [ramy150](https://github.com/ramy150)
* **Boukhalfa Mohammed** - *Improvement and optimization* - [mboukhalfa](https://github.com/mboukhalfa)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

