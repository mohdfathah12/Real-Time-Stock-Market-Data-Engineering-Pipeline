import pandas as pd
import boto3
import io


BUCKET_NAME = "your bucket name"
PROCESSED_PATH = f's3://{BUCKET_NAME}/transformed_data/stock_data.parquet'


def transform_data():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)

    all_data = []

    print("Fetching files from S3...")

    for obj in bucket.objects.all():
        if obj.key.endswith('.json'):

            content = obj.get()['Body'].read().decode('utf-8')
            try:
                data = pd.read_json(io.StringIO(content), lines=True)
                all_data.append(data)
            except:
                continue

    if not all_data:
        print("No JSON files found!")
        return

    df = pd.concat(all_data, ignore_index=True)

    print(f"Total rows collected: {len(df)}")
    print("Cleaning Data...")

    df.drop_duplicates(inplace=True)

    if 'price' in df.columns:
        df = df[df['price'] > 0]

    print(f"Saving transformed data to {PROCESSED_PATH}...")

    df.to_parquet(PROCESSED_PATH, engine='pyarrow', index=False)
    print("Done! Everything is cleaned and saved as Parquet.")


if __name__ == "__main__":
    import io

    transform_data()