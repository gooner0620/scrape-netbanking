#!/usr/bin/env python
# coding: utf-8

import time
import datetime
from selenium import webdriver
from models import Statement


class Mufg:
    """
    MUFGの入出金明細の照会結果画面をスクレイピングして
    入出金一覧を取得します
    """

    _MUFG_TOP_URL = 'https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login?_TRANID=AA000_001'

    def __init__(self, _id, _password):
        assert _id, 'ID is None'
        assert _password, 'password is None'
        self._id = _id
        self._password = _password
        self._browser = None
        self._statement_dict = {}
        self._total = 0

    def scrape(self):
        self._browser = webdriver.PhantomJS()
        try:
            self._login()
            if self._has_information():
                self._read_information()
            self._get_statements()
            self._logout()
        finally:
            self._browser.quit()

    def get(self, _date=None):
        if _date is None:
            return self._statement_dict
        return self._statement_dict.get(_date, [])

    @property
    def today(self):
        key = datetime.datetime.now().strftime('%Y%m%d')
        return self.get(key)

    @property
    def yesterday(self):
        key = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        return self.get(key)

    @property
    def total(self):
        return self._total

    def _login(self):
        self._browser.get(self._MUFG_TOP_URL)
        self._browser.find_element_by_id('account_id').send_keys(self._id)
        self._browser.find_element_by_id('ib_password').send_keys(self._password)
        self._browser.find_element_by_xpath('//img[@alt="ログイン"]').click()

    def _has_information(self):
        """
        ページタイトルからMUFGからのお知らせがあるかを判定します
        """
        return self._browser.title == 'お知らせ - 三菱東京ＵＦＪ銀行'

    def _read_information(self):
        """
        MUFGからお知らせを既読にします
        """
        while True:
            if not self._has_information():
                return

            information = self._browser.find_element_by_xpath(
                '//table[@class="data"]/tbody/tr')
            information.find_element_by_name('hyouzi').click()

            self._browser.find_element_by_xpath('//img[@alt="トップページへ"]').click()

    def _get_statements(self):
        """
        残高と入出金の明細を取得します
        """

        # 残高を取得
        total = self._browser.find_element_by_id('setAmountDisplay')
        self._total = self._yen_to_int(total.text)

        # 入出金明細画面に移動
        self._browser.find_element_by_xpath('//img[@alt="入出金明細をみる"]').click()

        # 明細一覧を取得
        banking_list = self._browser.find_elements_by_xpath(
            '//table[@class="data yen_nyushutsukin_001"]/tbody/tr')

        statement_dict = {}

        for banking in banking_list:
            detail = banking.find_elements_by_tag_name('td')

            _date = datetime.datetime.strptime(detail[0].text.replace('\n', ''),
                                               '%Y年%m月%d日')

            state = Statement(_date,
                              self._yen_to_int(detail[1].text),
                              self._yen_to_int(detail[2].text),
                              detail[3].text,
                              self._yen_to_int(detail[4].text))
            key = _date.strftime('%Y%m%d')

            if statement_dict.get(key) is None:
                statement_dict[key] = [state]
            else:
                t = statement_dict[key]
                t.append(state)

        self._statement_dict = statement_dict

    def _yen_to_int(self, yen):
        """カンマと「円」を削除します"""
        if yen == '':
            return 0
        return int(yen.replace(',', '').replace('円', ''))

    def _logout(self):
        self._browser.find_element_by_link_text('ログアウト').click()
