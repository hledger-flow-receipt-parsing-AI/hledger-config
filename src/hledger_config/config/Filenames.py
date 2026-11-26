import os
from dataclasses import dataclass

from hledger_config.config.DirPathsConfig import DirPathsConfig
from hledger_config.config.ReceiptImgConfig import ReceiptImgConfig


@dataclass
class FileNames:
    start_journal_filepath: str
    root_journal_filename: str
    tui_label_filename: str
    receipt_img: ReceiptImgConfig
    categories_filename: str
    # The one-hot categorisation rules of the bank transactions, next to
    # the categories in the finance root.
    categorisation_rules_filename: str = "categorisation_rules.yaml"

    def get_filepath(
        self, dir_path_config: DirPathsConfig, filename: str
    ) -> str:
        if filename == "root_journal_filename":
            root_journal_dir_path: str = dir_path_config.get_path(
                path_name="working_subdir", absolute=True
            )
            return os.path.join(
                root_journal_dir_path, self.root_journal_filename
            )
        elif filename == "categories_filename":
            root_finance_path: str = dir_path_config.get_path(
                path_name="root_finance_path", absolute=True
            )
            return os.path.join(root_finance_path, self.categories_filename)
        elif filename == "categorisation_rules_filename":
            root_finance_path = dir_path_config.get_path(
                path_name="root_finance_path", absolute=True
            )
            return os.path.join(
                root_finance_path, self.categorisation_rules_filename
            )
        else:
            raise NotImplementedError(
                f"Don't yet know how to get the filepath of:{filename}"
            )
