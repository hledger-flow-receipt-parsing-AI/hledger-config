"""Parses the CLI args."""

import argparse
import re

from typeguard import typechecked


@typechecked
def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Triodos Bank CSV to custom format."
    )

    # Data arguments
    parser.add_argument(
        "-p",
        "--pre-processed-output-dir",
        type=str,
        required=False,
        help="The dir name containing the pre-processed csv files..",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        help="Path to config file.",
    )

    parser.add_argument(
        "-e",
        "--edit-receipt",
        action="store_true",
        required=False,
        help="Edit a receipt in TUI.",
    )

    # Action arguments
    # Action 0.
    parser.add_argument(
        "-n",
        "--new-setup",
        action="store_true",
        required=False,
        help=(
            "Use this flag if you want to add a new account for double-entry"
            " book keeping."
        ),
    )

    # Action 1.
    parser.add_argument(
        "-o",
        "--preprocess-csvs",
        action="store_true",
        required=False,
        help=(
            "Convert the csv from the bank to csvs that hledger-flow can read."
        ),
    )

    # Action 2.
    parser.add_argument(
        "-r",
        "--generate-rules",
        required=False,
        action="store_true",
        help="Generates the .rules file for hledger flow imports.",
    )

    # Action 3.a
    parser.add_argument(
        "-t",
        "--tui-label-receipts",
        action="store_true",
        required=False,
        help=(
            "Manually make the labels for the receipt images that do not have a"
            " manual label yet."
        ),
    )

    # Action 3.b
    parser.add_argument(
        "-a",
        "--make-ai-labels",
        action="store_true",
        required=False,
        help=(
            "Use AI models to convert the  receipt images into Receipt objects"
            " for receipt images that do not have an AI label yet."
        ),
    )

    # Action 3.c
    parser.add_argument(
        "-i",
        "--improve-manual-labels",
        action="store_true",
        required=False,
        help=(
            "Manually improve the existing manual labels for the receipt"
            " images."
        ),
    )

    # Action 4.
    parser.add_argument(
        "-l",
        "--link-receipts-to-transactions",
        action="store_true",
        required=False,
        help=(
            "Link the receipt images to the accompanying (if any) transaction"
            " of your bank csv to prevent duplicate entries. Can only be done"
            " after .csv pre-processing and after all receipt images are"
            " converted to receipt objects."
        ),
    )
    parser.add_argument(
        "-s",
        "--preprocess-assets",
        action="store_true",
        required=False,
        help="Make hledger-flow preprocess the exported asset csvs.",
    )

    # Action 5: Batch match receipts to CSV transactions (non-interactive).
    parser.add_argument(
        "-b",
        "--match-receipts",
        action="store_true",
        required=False,
        help=(
            "Batch-match existing receipt labels to bank CSV transactions."
            " Auto-links exact matches and warns on ambiguous/missing ones."
            " Should run before --preprocess-assets so that withdrawal"
            " metadata is available when bank CSVs are processed."
        ),
    )

    # Action 6: Match linked-account CSV transactions to each other.
    parser.add_argument(
        "--match-csv-to-csv",
        action="store_true",
        required=False,
        help=(
            "Reconcile linked-account CSV transactions. Auto-matches"
            " same-currency transfers; prompts for cross-currency ones."
        ),
    )

    # Umbrella: run both receipt matching and CSV-to-CSV matching.
    parser.add_argument(
        "--match-transactions",
        action="store_true",
        required=False,
        help=(
            "Run all transaction matching: receipt-to-CSV (--match-receipts)"
            " and CSV-to-CSV (--match-csv-to-csv)."
        ),
    )

    # CSV column mapping.
    parser.add_argument(
        "-m",
        "--map-csv",
        type=str,
        required=False,
        help=(
            "Path to a CSV file whose columns you want to interactively map"
            " to transaction fields. The mapping is saved into your config."
        ),
    )

    # Pre-flight checks (US-4.6 and US-4.7).
    parser.add_argument(
        "--check-categorisation",
        action="store_true",
        required=False,
        help=(
            "Dry-run categorisation check: load all bank CSV transactions and"
            " verify each can be categorised by the rule-based model. Exits"
            " non-zero if any uncategorised transactions are found."
        ),
    )
    parser.add_argument(
        "--check-matching",
        action="store_true",
        required=False,
        help=(
            "Report which receipt transactions are still unlinked to CSV"
            " transactions. If unlabelled receipt images exist, hints that"
            " the missing match may be there. Informational only (exits 0)."
        ),
    )
    parser.add_argument(
        "--check-categorisation-overlap",
        action="store_true",
        required=False,
        help=(
            "Check that categorisation rules are one-hot: each transaction"
            " matches at most one rule. Reports transactions where multiple"
            " rules match (order-dependent categorisation). Exits non-zero"
            " if any overlaps are found."
        ),
    )

    # Debugging functionality.
    parser.add_argument(
        "-q",
        "--quick-categorisation",
        action="store_true",
        required=False,
        help=(
            "Quickly get feedback on unidentified transactions to quickly"
            " create (private) categorisation rules."
        ),
    )

    # Full pipeline (replaces start.sh).
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        required=False,
        help=(
            "Run the full preprocessing pipeline: validate config, set up"
            " accounts, check categorisation, match transactions, preprocess"
            " assets, run hledger-flow import, and generate balance report."
            " Replaces the old start.sh shell script."
        ),
    )
    parser.add_argument(
        "--randomize",
        action="store_true",
        required=False,
        help=(
            "When used with --run-pipeline, randomize financial data before"
            " plotting (for demos/screenshots)."
        ),
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        required=False,
        help=(
            "When used with --run-pipeline, skip interactive steps (e.g."
            " cross-currency CSV-to-CSV matching TUI prompts). Useful for"
            " automated testing and CI."
        ),
    )

    # Receipt grouping: group duplicate images before labelling.
    parser.add_argument(
        "--group-receipts",
        action="store_true",
        required=False,
        help=(
            "Interactively group duplicate receipt images before labelling. "
            "Identical images are auto-grouped by content hash; remaining "
            "images are shown for manual grouping (n=new, g=group, p=prime, "
            "s=skip). Can be used standalone or with --tui-label-receipts."
        ),
    )
    parser.add_argument(
        "--regroup",
        action="store_true",
        required=False,
        help=(
            "Force re-grouping even if a saved grouping exists. "
            "Used with --group-receipts."
        ),
    )

    # AI: skip suggestions in TUI.
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        required=False,
        help=(
            "Skip AI suggestion inference when labelling receipts"
            " (used with --tui-label-receipts). Saves power and"
            " startup time."
        ),
    )

    # hledger-ai: train the locally trained receipt suggestion models.  The
    # flag lives here because hledger_preprocessor's parser does; hledger-ai
    # does the work (and takes the same names on its own command line).
    parser.add_argument(
        "--train",
        nargs="*",
        metavar="NAME",
        default=None,
        required=False,
        help=(
            "Train the receipt suggestion models that are out of date."
            " With names, only those models (e.g. rapidocr-linear) and"
            " strategies (e.g. ST-1)."
        ),
    )

    # AI model training.
    parser.add_argument(
        "--train-models",
        action="store_true",
        required=False,
        help=(
            "Train/retrain AI models on accumulated labelled data."
            " Skips training if dataset unchanged since last run."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["setfit", "qwen-lora", "all"],
        default="all",
        required=False,
        help=(
            "Which AI model to train (used with --train-models)."
            " Default: all eligible models."
        ),
    )
    parser.add_argument(
        "--force-retrain",
        action="store_true",
        required=False,
        help=(
            "Force retraining even if the dataset hash hasn't"
            " changed (used with --train-models)."
        ),
    )

    return parser


def assert_has_only_valid_chars(*, input_string: str) -> None:
    # a-Z, underscore, \, /.
    valid_chars = re.compile(r"^[a-zA-Z0-9_/\\]*$")
    assert valid_chars.match(
        input_string
    ), f"Invalid characters found in: {input_string}"


@typechecked
def assert_args_are_valid(*, args: argparse.Namespace) -> None:
    if args.quick_categorisation:
        if not args.preprocess_csvs:
            raise ValueError(
                "To quickly create new .csv transaction categorisation rules,"
                " you need to include the --preprocess-csvs arg and the"
                " --pre-processed-output-dir."
            )
    if args.preprocess_csvs:
        if args.pre_processed_output_dir is None:
            raise ValueError(
                "The pre_processed_output_dir arg is required for"
                " preprocess_csvs."
            )
