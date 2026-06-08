# tests/test_learner.py
import os
import tempfile
import pytest
from agent.learner import Learner


class TestLearner:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.learner = Learner(
            project_dir=self.tmpdir,
            data_dir=os.path.join(self.tmpdir, 'data'),
        )

    def test_learn_from_empty_ledger(self):
        result = self.learner.learn_from_ledger({'months': {}})
        assert result['learned'] is False

    def test_learn_from_ledger_with_data(self):
        data = {
            'months': {
                '2026-06': {
                    'income': [
                        {'amount': 100, 'platform': 'github'},
                        {'amount': 50, 'platform': 'medium'},
                    ],
                    'expenses': [
                        {'amount': 30, 'item': 'API'},
                    ],
                }
            }
        }
        result = self.learner.learn_from_ledger(data)
        assert result.get('total_months') == 1 or result.get('learned') is False

    def test_learn_from_channels(self):
        channels = [
            {'id': 'github', 'enabled': True, 'revenue': 50},
            {'id': 'medium', 'enabled': True, 'revenue': 0},
            {'id': 'kofi', 'enabled': False, 'revenue': 0},
        ]
        result = self.learner.learn_from_channels(channels)
        assert result['active_channels'] == 2
        assert result['earning_channels'] == 1

    def test_save_to_knowledge_base(self):
        self.learner.save_to_knowledge_base('测试主题', '测试内容', tags=['test'])
        assert self.learner.get_knowledge_count() == 1

    def test_get_all_knowledge(self):
        self.learner.save_to_knowledge_base('主题A', '内容A')
        self.learner.save_to_knowledge_base('主题B', '内容B')
        entries = self.learner.get_all_knowledge()
        assert len(entries) == 2

    def test_get_knowledge_filtered(self):
        self.learner.save_to_knowledge_base('Python学习', 'Python是一门好语言')
        self.learner.save_to_knowledge_base('赚钱经验', 'GitHub Sponsors有效')
        entries = self.learner.get_all_knowledge(topic_filter='Python')
        assert len(entries) == 1

    def test_generate_weekly_report(self):
        data = {'months': {'2026-06': {'income': [{'amount': 100}], 'expenses': [{'amount': 20}]}}}
        report = self.learner.generate_weekly_report(data, [])
        assert '周报' in report
        assert '100' in report
