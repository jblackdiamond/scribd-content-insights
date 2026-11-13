# Scribd Content Insights

For the Scribd take-home exercise, I explored how employees could ask analytics questions in everyday language and get answers based on clearly defined, checked metrics.

## Start here

- **Executive summary:** Included as a separate PDF with my submission. It describes the approach, key findings, tradeoffs, and proposed AI design.
- **Streamlit demo:** The live link is included in my submission email. [Application source](app.py)
- **[Metric dictionary and data-quality notes](documentation/metric_dictionary.md):** What each metric counts, which records qualify, and what the data cannot reliably tell us.
- **[Analysis scripts](analysis/):** Python calculations supporting the results.
- **[Test cases](tests/test_routing.py)** and [example questions](documentation/prototype_test_questions.md): Checks for supported and unsupported questions.

## Approach

I started with the six supplied tables in [`data/raw/`](data/raw/), checking duplicates, test records, missing relationships, unexpected values, and events dated before signup. I documented my choices, then calculated and checked the metrics in Python. The app reads the certified aggregate CSVs in [`data/`](data/), rather than inventing figures in its responses.

The data is synthetic and some definitions aren't provided. For example, a content interaction isn't proof that someone read or listened to the content, and a subscription start isn't necessarily a new paying customer. The metric dictionary explains where assumptions affect the results.

## Prototype and proposed AI design

The current Streamlit demo is intentionally **rule-based, not LLM-powered**. It recognizes a limited set of questions, looks up certified metrics, and shows explanations and relevant caveats. Unsupported questions shouldn't produce guessed answers.

For an LLM-based version, I would use the model to interpret the question and identify the intended metric, filters, and date range. The system would then verify that request against approved definitions and calculate the numbers separately. The LLM could explain the result, but shouldn't silently choose a different metric or invent figures.

## Run the demo locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app uses the certified CSVs under `data/`. **No API key is needed.**

## Reproducing the analysis

The original source CSVs are preserved under [`data/raw/`](data/raw/), with calculation scripts in [`analysis/`](analysis/).

- `scribd_certify_metrics.py` was originally written to run alongside the six raw CSVs. For reproduction, copy the script to a separate temporary directory with copies of the raw CSVs, run it there, and compare its outputs to the committed certified results.
- `certify_additional_metrics.py` accepts the path to the raw-data directory as an argument. It writes aggregate outputs to the repository's `data/` directory, so review changes before overwriting the reference CSVs.

The scripts and certified outputs are included to make the analytical work inspectable, not as a production data pipeline.

## Important limitations

- Some content items have no linked creator. The count of known linked creators isn't necessarily a complete author count.
- The current model excludes engagement events dated before their user's signup. That is an explicit assumption that could be revisited if pre-signup activity is valid.
- Subscription status is a snapshot and cannot, on its own, establish historical active subscribers.
- I have not treated monthly recurring revenue, reading time, or completion rate as reliable measures from the information provided.
- This demo does not include live data refresh, production user permissions, or an independently enforced metrics service.
