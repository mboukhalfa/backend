# MIRA! Project

MIRA! is a framework of live migration.


### Installing

Activate virtual env


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

Run Django


```
python manage.py runserver
```


## Shutdown

Shutdown celery worker


```
celery -A mirai_project control shutdown
```

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [DRF](https://www.django-rest-framework.org/) - Used to generate REST API
* [Pipenv](https://pipenv.readthedocs.io/en/latest/) - Dependency Management


## Authors
* **Rami Akrem Addad** - *Initial work* - [ramy150](https://github.com/ramy150)
* **Mohammed Boukhalfa** - *Improvement and optimization* - [mboukhalfa](https://github.com/mboukhalfa)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

