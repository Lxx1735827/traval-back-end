from src.schema import *
import copy
import itertools

Min_Sup = 0.2
Min_Conf = 1.5
supports = {}


async def load_data():
    users = await User.all()
    sites_all_users = []
    for user in users:
        sites = await user.sites.all()
        site_ids1 = [site.id for site in sites]
        sites = await user.sites.all()
        site_ids2 = [site.id for site in sites]
        user_sites = tuple(set(site_ids1).union(set(site_ids2)))
        sites_all_users.append(user_sites)
    return sites_all_users


def one_set(datas):
    """
    生成1项集
    :param datas: 数据 集合列表
    :return: 1项集
    """
    one_support = {}
    for i in range(0, len(datas)):
        for j in range(0, len(datas[i])):
            if datas[i][j] in one_support.keys():
                one_support[datas[i][j]] += 1
            else:
                one_support[datas[i][j]] = 1
    ones = set()
    for key in one_support.keys():
        one_support[key] /= len(datas)
        if one_support[key] >= Min_Sup:
            temp_set = frozenset([key])
            ones.add(temp_set)
            supports[frozenset([key])] = one_support[key]
    return ones


def items(ones, datas):
    temps = [ones]
    temp_sets = copy.deepcopy(ones)
    while len(temp_sets) > 1:
        new_temp_set = set()
        for one1 in temp_sets:
            for one2 in temp_sets:
                temp_set = one1.union(one2)
                if temp_set not in new_temp_set and len(temp_set) == len(one1)+1:
                    temp_item = 0
                    for i in range(0, len(datas)):
                        if temp_set <= frozenset(datas[i]):
                            temp_item += 1
                    if temp_item/len(datas) >= Min_Sup:
                        supports[frozenset(temp_set)] = temp_item/len(datas)
                        new_temp_set.add(temp_set)
        if len(new_temp_set) > 0:
            temps.append(frozenset(new_temp_set))
        temp_sets = new_temp_set
    return temps


def rule(items_):
    rules = []
    for i in range(1, len(items_)):
        for j in range(0, len(items_[i])):
            for k in range(1, i+1):
                for subset in itertools.combinations(items_[i][j], k):
                    subset2 = items_[i][j]-set(subset)
                    if frozenset(subset) in supports.keys() and frozenset(subset2) in supports.keys():
                        if supports[frozenset(subset2)]/supports[frozenset(items_[i][j])] >= Min_Conf:
                            rules.append([set(subset), subset2])
    return rules


async def insert_data():
    data = await load_data()
    support_items = items(one_set(data), data)
    support_rules = []
    for i in range(0, len(support_items)):
        support_rule = []
        for j in support_items[i]:
            support_rule.append(set(j))
        support_rules.append(support_rule)
    ends = rule(support_rules)
    for end in ends:
        site_ids1 = ""
        for site_id in end[0]:
            site_ids1 += str(site_id) + "*"
        site_ids2 = ""
        for site_id in end[1]:
            site_ids2 += str(site_id) + "*"

        record = await SiteRelationship.get_or_none(site_from_ids=site_ids1)
        if record is None:
            print(record)
            await SiteRelationship.create(site_from_ids=site_ids1, site_to_ids=site_ids2)
        else:
            record.site_to_ids = site_ids2
            await record.save()


if __name__ == "__main__":
    insert_data()