import time
import argparse
from scraper import Scraper
from compile import compile_data
from s3upload import S3Helper

def main(stamp_date):
    keywords = ["smart phone", "laptop", "camera", "headphones", "smart watch", "tablet", "television", "shoes", "clothes", "shirts", "jeans", "t-shirts", "watches", "bags", "wallets", "sunglasses", "toys", "games", "books", "laptops", "mobiles", "cameras", "headphones", "speakers", "shoes", "clothes"]
    amazon = Scraper()

    for i in keywords:
        amazon.search(i, stamp_date)

    print("Compiling data")
    time.sleep(1)
    #amazon.search("smart phone")
    compile_data(stamp_date)
    time.sleep(1)
    print("Uploading to S3")
    s3 = S3Helper()
    s3.upload(stamp_date)
    print("Done")

if __name__ == "__main__":

    # run the above function every 5 minutes
    while True:
        stamp_date = time.strftime("%Y-%m-%d-%H-%M-%S")
        print("Extracting...")
        start = time.perf_counter()
        main(stamp_date)
        stop = time.perf_counter()
        time.sleep(60*5)
        print("Finished Extracting...")
        print(f"The extraction took {stop - start}")

        # stop the program after 1 hour
        if time.perf_counter() > 60*60:
            break
        