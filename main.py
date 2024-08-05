import pandas as pd
from multiprocessing import Pool
from crawling_parsing.crawling_arch import (
    DaumMovingElementLocation,
    GoogleMovingElementsLocation,
)


def csv_saving(data: list, csv_file_name: str) -> pd.DataFrame:
    """Coin symbol CSV saving

    Args:
        data (list): Coin symbol
        csv_file_name (str): File name

    Returns:
        pd.DataFrame: DataFrame
    """
    print(f"Saving data to {csv_file_name}")
    pd.DataFrame(data).to_csv(
        csv_file_name,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Data saved to {csv_file_name}")
    return pd.DataFrame(data)


def flattened_data(data):
    return [item for sublist in data for item in sublist]


def save_csv_for_daum():
    try:
        print("Fetching Daum data...")
        daum_data = DaumMovingElementLocation("쿠팡페이 사업", 3).page_news_data_glean()
        data = flattened_data(daum_data)
        csv_saving(data, "news_data_daum.csv")
    except Exception as e:
        print(f"Error in save_csv_for_daum: {e}")


def save_csv_for_google():
    try:
        print("Fetching Google data...")
        google_data = GoogleMovingElementsLocation("쿠팡페이 사업", 3).search_box()
        data = flattened_data(google_data)
        csv_saving(data, "news_data_google.csv")
    except Exception as e:
        print(f"Error in save_csv_for_google: {e}")


if __name__ == "__main__":
    try:
        # Use multiprocessing Pool to run tasks in parallel
        with Pool(processes=2) as pool:
            pool.apply_async(save_csv_for_daum)
            pool.apply_async(save_csv_for_google)
            pool.close()
            pool.join()
    except Exception as e:
        print(f"Error in multiprocessing: {e}")
