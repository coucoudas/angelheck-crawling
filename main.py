import pandas as pd
from crawling_parsing.crawling_arch import DaumMovingElementLocation


def csv_saving(data: list, csv_file_name: str) -> pd.DataFrame:
    """coin symbol csv saving

    Args:
        data (list): coinsymbol
        csv_file_name (str): 파일명

    Returns:
        pd.DataFrame: dataframe
    """
    return pd.DataFrame(data).to_csv(
        csv_file_name,
        index_label=False,
        index=False,
        encoding="utf-8-sig",
    )


data = DaumMovingElementLocation("쿠팡파이낸셜", 2).page_news_data_glean()

flattened_data = [item for sublist in data for item in sublist]

# CSV 파일로 저장합니다.
csv_saving(data=flattened_data, csv_file_name="news_data.csv")
