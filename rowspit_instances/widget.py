"""
Orange widget for splitting rows that have more than one instance of data
to separate rows
"""

import sys
import numpy as np
from typing import Optional

from Orange.data import Table, Domain, ContinuousVariable, Instance
from AnyQt.QtWidgets import (
    QSizePolicy, QComboBox, QPushButton
)

from Orange.widgets import gui
from Orange.widgets.utils import itemmodels
from Orange.widgets.widget import OWWidget, Input, Output


class OWSplitInstancesWidget(OWWidget):
    """
    Widget for splitting instances.
    If we have dataset with "quantity" column we can multiply that row
    number of times it is present fo r example:
    Name | product  | quantity
    John | icecream | 3
    Lisa | pie      | 2
    Will be transformed to:
    Name | product
    John | icecream
    John | icecream
    John | icecream
    Lisa | pie
    Lisa | pie
    """
    # Widget's name as displayed in the canvas
    name = "Split instances"
    # Short widget description
    description = "Lets the user input a number"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "../img/icon.svg"
    category = "Data"

    class Inputs:
        """Input fields definition"""
        data = Input("Data", Table)

    class Outputs:
        """Output fields definition"""
        data = Output("Data", Table)

    def __init__(self):
        self.data = None
        # List of all features (model for ComboBox)
        self.features = itemmodels.VariableListModel(
            ["Select Feature"], parent=self)

        box = gui.vBox(self.controlArea, "Select ")
        self.features_widget = QComboBox(
            self.controlArea,
            minimumContentsLength=16,
            sizeAdjustPolicy=QComboBox.AdjustToMinimumContentsLengthWithIcon,
            sizePolicy=QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        )
        self.features_widget.setModel(self.features)
        self.features_widget.currentIndexChanged.connect(self.feature_changed)
        self.button = QPushButton("Split")
        self.button.clicked.connect(self.split)
        self.button.setEnabled(False)

        box.layout().addWidget(self.features_widget)
        box.layout().addWidget(self.button)

    @Inputs.data
    def set_data(self, data: Table):
        """
        Handler for input data
        :param data: Input Orange Table
        :return: None
        """
        self.data = data
        self.features[:] = ["Select Feature"]
        if self.data \
                and self.data.domain is not None \
                and not self.data.domain.empty():
            self.features[:] += [
                var for var in self.data.domain.variables
                if self.is_integer_col(var)
            ]  # only integer columns may be quantity columns

    def selected_col(self)->Optional(str):
        """
        Get selected feature value
        :return: Selected feature name r None if Nothing selected
        """
        index = self.features_widget.currentIndex()
        if index < 1:
            return None
        return self.features[index]

    def feature_changed(self):
        """
        Handler for changed selected feature value in ComboBox
        :return: None
        """
        if self.selected_col():
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def handleNewSignals(self):
        if self.data is None:
            self.Outputs.data.send(None)
        else:
            self.feature_changed()

    def split(self):
        """
        Function for splitting provided data
        :return: None
        """
        col = self.selected_col().name

        # all columns except quantity
        without_count_col = tuple(
            var for var in self.data.domain.variables
            if var.name != col
        )
        # domain without quantit column
        new_domain = Domain(
            without_count_col,
            self.data.domain.class_vars,
            self.data.domain.metas
        )

        res = Table.from_domain(
            new_domain
        )
        for row in self.data:
            res.append(Instance(new_domain, row))
            rows_added = 1
            if not np.isnan(row[col]):
                while rows_added < row[col]:
                    res.append(Instance(new_domain, row))
                    rows_added += 1
        self.Outputs.data.send(res)

    def is_integer_col(self, name: str)->bool:
        """
        Check if provided column is integer
        :param name: column name
        :return: is column integer or not
        """
        if not isinstance(self.data.domain[name], ContinuousVariable):
            return False
        return all([
            np.isnan(row[name])  # we count NaN columns as qty 1
            or np.equal(np.mod(row[name], 1), 0)  # check that column is integer
            for row in self.data
        ])


def main(argv=None):
    """
    Test as separate Qt application
    :param argv: arguments from console - DataSet name if provided
    :return: None
    """
    from AnyQt.QtWidgets import QApplication
    # PyQt changes argv list in-place
    app = QApplication(list(argv) if argv else [])
    argv = app.arguments()
    if len(argv) > 1:
        filename = argv[1]
    else:
        filename = "housing"

    ow = OWSplitInstancesWidget()
    ow.show()
    ow.raise_()

    dataset = Table(filename)
    ow.set_data(dataset)
    ow.handleNewSignals()
    app.exec_()
    ow.set_data(None)
    ow.handleNewSignals()
    ow.onDeleteWidget()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))