def test_find_assets(self):
        """Test finding assets by search string"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            
            response = a_client.find_assets(search_string="Postgres", output_format="JSON")
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nFound {len(response) if isinstance(response, list) else 0} assets")
            
            assert True
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except Exception as e:
            console.print_exception(e)
            assert False, "Unexpected error"
        finally:
            a_client.close_session()