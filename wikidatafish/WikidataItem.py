#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Convert data to a Wikidata item."""
from wikidataStuff.WikidataStuff import WikidataStuff as WDS
from wikidataStuff import helpers as helpers
import pywikibot

import utils

DATA_DIR = "data"


class WikidataItem(object):
    """A converter for a single piece of data to Wikidata format."""

    def __init__(self, db_row_dict, repository, data_files, existing):
        """
        Initiate the object.

        :param db_row_dict: piece of raw to be converted to one WD item
        :param repository: data repository of site to work on (Wikidata)
        :param data_files: dictionaries of mappings etc.
        :param existing: dictionary of existing WD items with certain prop
        """
        self.repo = repository
        self.existing = existing
        self.wdstuff = WDS(self.repo)
        self.raw_data = db_row_dict
        self.props = data_files["properties"]
        self.construct_wd_item()

        self.problem_report = {}

    def make_q_item(self, qnumber):
        """
        Convert a Wikidata Q to a page object.

        :param qnumber: a Q ID, either with or
        without the 'Q'.
        """
        return self.wdstuff.QtoItemPage(qnumber)

    def make_pywikibot_item(self, value):
        """
        Convert data structure to pywikibot object.

        :param value: content of statement
        :type value: a string (for text), a string
                     representing a Q ID (for WD item),
                     a dictionary
                     (with either "quantity_value" or
                     "date_value" as key), a "somevalue"
                     or "novalue" for special types;
                     alternatively a single-element
                     list of any of these.
        """
        val_item = None
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        if utils.string_is_q_item(value):
            val_item = self.make_q_item(value)
        elif isinstance(value, dict) and 'quantity_value' in value:
            number = value['quantity_value']
            if 'unit' in value:
                unit = self.wdstuff.QtoItemPage(value["unit"])
            else:
                unit = None
            val_item = pywikibot.WbQuantity(
                amount=number, unit=unit, site=self.repo)
        elif isinstance(value, dict) and 'date_value' in value:
            date_dict = value["date_value"]
            val_item = pywikibot.WbTime(year=date_dict.get("year"),
                                        month=date_dict.get("month"),
                                        day=date_dict.get("day"))
        elif value in ["somevalue", "novalue"]:
            val_item = value
        else:
            val_item = value
        return val_item

    def make_statement(self, value):
        """
        Make a statement.

        :param value: content of statement
        """
        if value in ['somevalue', 'novalue']:
            special = True
        else:
            special = False
        return self.wdstuff.Statement(value, special=special)

    def make_qualifier_applies_to(self, value):
        """
        Create 'applies to part' qualifier object.

        :param value: what part this applies to (Q item)
        """
        prop_item = self.props["applies_to_part"]
        target_item = self.wdstuff.QtoItemPage(value)
        return self.wdstuff.Qualifier(prop_item, target_item)

    def add_statement(self, prop_name, value, quals=None, ref=None):
        """
        Add a statement to the data object.

        :param prop_name: name of property, as stated in mapping file.
        :param value: content of statement
        :param qual: qualifier(s) to include
        :param ref: reference to include
        """
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if quals is None:
            quals = []
        wd_claim = self.make_pywikibot_item(value)
        statement = self.make_statement(wd_claim)
        for qual in helpers.listify(quals):
            statement.addQualifier(qual)
        base.append({"prop": prop,
                     "value": statement,
                     "ref": ref})

    def make_stated_in_ref(self,
                           value,
                           pub_date=None,
                           ref_url=None,
                           retrieved_date=None):
        """
        Create a 'stated in' referene.

        :param value: content of reference (Q item)
        :param pub_date: publication date (optional)
        :param ref_url: reference URL (optional)
        :param retrieved_date: date when information was retrieved (optional)
        """
        item_prop = self.props["stated_in"]
        published_prop = self.props["publication_date"]
        published_claim = None
        if pub_date:
            pub_date = utils.date_to_dict(pub_date, "%Y-%m-%d")
            timestamp = self.make_pywikibot_item({"date_value": pub_date})
            published_claim = self.wdstuff.make_simple_claim(
                published_prop, timestamp)
        source_item = self.wdstuff.QtoItemPage(value)
        source_claim = self.wdstuff.make_simple_claim(item_prop, source_item)
        if ref_url and retrieved_date:
            ref_url_prop = self.props["reference_url"]
            retrieved_date_prop = self.props["retrieved"]

            retrieved_date = utils.date_to_dict(retrieved_date, "%Y-%m-%d")
            retrieved_date = self.make_pywikibot_item(
                {"date_value": retrieved_date})

            ref_url_claim = self.wdstuff.make_simple_claim(
                ref_url_prop, ref_url)
            retrieved_on_claim = self.wdstuff.make_simple_claim(
                retrieved_date_prop, retrieved_date)

            if published_claim:
                ref = self.wdstuff.Reference(
                    source_test=[source_claim, ref_url_claim],
                    source_notest=[published_claim, retrieved_on_claim])
            else:
                ref = self.wdstuff.Reference(
                    source_test=[source_claim, ref_url_claim],
                    source_notest=[retrieved_on_claim])
        else:
            ref = self.wdstuff.Reference(
                source_test=[source_claim],
                source_notest=published_claim
            )
        return ref

    def associate_wd_item(self, wd_item):
        """
        Associate this data object with WD item.

        :param wd_item: Q ID of WD item
        """
        if wd_item is not None:
            self.wd_item["wd-item"] = wd_item

    def set_upload(self, booln):
        """Set whether this object shall be uploaded to Wikidata."""
        self.wd_item["upload"] = booln

    def add_label(self, language, text):
        """
        Add a label in certain language.

        :param language: code of language, e.g. "fi"
        :param text: content of label
        """
        base = self.wd_item["labels"]
        base.append({"language": language, "value": text})

    def add_description(self, language, text):
        """
        Add a description in certain language.

        :param language: code of language, e.g. "fi"
        :param text: content of description
        """
        base = self.wd_item["descriptions"]
        base.append({"language": language, "value": text})

    def construct_wd_item(self):
        """Create the empty structure of the data object."""
        self.wd_item = {}
        self.wd_item["upload"] = False
        self.wd_item["statements"] = []
        self.wd_item["labels"] = []
        self.wd_item["descriptions"] = []
        self.wd_item["wd-item"] = None
