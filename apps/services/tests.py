from django.test import TestCase


class ServicesTest(TestCase):

    def test_example_service_greet(self):
        from .services import ExampleService

        s = ExampleService()
        self.assertEqual(s.greet('Andres'), 'Hola, Andres')
