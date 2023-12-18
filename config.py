FIRST_PLACE_PATH = "//h4[contains(text(), '1등 배출점')]/ancestor::div[@class='group_content']/table[@class='tbl_data tbl_data_col']"
SECOND_PLACE_PATH = "//h4[contains(text(), '2등 배출점')]/ancestor::div[@class='group_content']/table[@class='tbl_data tbl_data_col']"
PAGINATION_LINK_PATH = "//div[@id='page_box']//a"
DATABASE_URL = "postgresql://postgres:lotto@localhost:5432/lotto"