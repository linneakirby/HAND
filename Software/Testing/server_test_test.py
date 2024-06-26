import unittest
import server_test

class Server_Test_Test(unittest.TestCase):

    app = server_test.create_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get("/hand")
        assert response.status_code == 200
        assert "0.8 0.4 0.0 0.0 " == response.get_data(as_text=True)

if __name__ == "__main__":
    unittest.main()