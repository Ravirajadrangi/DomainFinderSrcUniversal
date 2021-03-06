from multiprocessing import Event
import queue
from unittest import TestCase
from DomainFinderSrc.MajesticCom import *
from DomainFinderSrc.SiteConst import *
from DomainFinderSrc.Scrapers.MatrixFilter import MajesticFilter
from DomainFinderSrc.Scrapers.SiteTempDataSrc.DataStruct import FilteredDomainData
from DomainFinderSrc.Utilities import FileIO, Logging, FilePath
from DomainFinderSrc.ComboSites.GoogleMajetic import GoogleMajestic, GoogleCom
from DomainFinderSrc.MajesticCom.Category import *
from UnitTest.Accounts import majestic, majestic_account
from DomainFinderSrc.MiniServer.DatabaseServer.CategoryDB import CategoryDBManager
from DomainFinderSrc.MiniServer.DatabaseServer.CategorySiteDB import CategorySeedSiteDB, CategorySiteDBManager
from DomainFinderSrc.Utilities.Serializable import Serializable
from DomainFinderSrc.MiniServer.Common.DBInterface import *
import re


def parse_majestic_topic(topics: str) -> [SubCategory]:
    splited_topics = topics.split(";")
    catagories = []
    for item in splited_topics:
        if len(item) == 0:
            continue
        topic, trust_flow = item.split(":")
        if len(topic) == 0 or len(trust_flow) == 0:
            continue
        else:
            parsed_catagory = CategoryManager.decode_sub_category(topic)
            catagories.append(parsed_catagory)
            print(parsed_catagory)
    return catagories


def is_valid_ISO8859_1_str(original_str: str) -> bool:
    try:
        temp = original_str.encode(encoding='iso-8859-1').decode(encoding='iso-8859-1')
        if temp == original_str:
            return True
        else:
            return False
    except:
        return False


def convert_to_regular_expression(keyword: str):
    if is_valid_ISO8859_1_str(keyword):
        pass


def backlink_callback(backlink: MajesticBacklinkDataStruct):
    logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/Gambling3.csv"
    print(backlink)
    Logging.CsvLogger.log_to_file_path(logging_path, [backlink.to_tuple(), ])


class MajesticTest(TestCase):

    def testTF_CF(self):
        data = majestic.get_cf_tf_list(["www.articleroller.com", "http://www.articleroller.com"], True)
        for item in data:
            print(item)

    def test_anchor_text(self):
        data = majestic.get_anchor_text_info(domain="susodigital.com", is_dev=False)
        print(data)
        print("number of data points: ", len(data[0]))

    def test_ref_domains(self):
        data = majestic.get_ref_domains(domain="ukcriminallawblog.com", max_count=100, is_dev=False, fresh_data=True)
        counter = 0
        for item in data:
            print("counter:", counter, " item:", str(item))
            counter += 1


    def testWesternLan(self):
        strs = ["travel log", "something", "中国字", "Агент Mail.Ru", "conférence des communautés homosexuelle"]
        for original_str in strs:
            print(original_str, " is valid?:", is_valid_ISO8859_1_str(original_str))

    def test_filter_ref_domain(self):
        def _filter_ref_domains(domain: str) -> bool:
            max_bad_country_ratio = 0.1
            bad_country_count = 0
            max_backlinks_for_single_bad_country = 30
            _bad_country = ["CN", "JP", "KO", "RU"]
            ref_domains = []
            ref_domains.append(MajesticRefDomainStruct("bbc.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("cnn.org", tf=70, cf=67, country="US", backlinks=4000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("csa.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("sina.org", tf=70, cf=67, country="CN", backlinks=25, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("bbc.co.jp", tf=99, cf=78, country="JP", backlinks=10, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("ahref.com", tf=70, cf=67, country="CN", backlinks=20, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("bbc.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("cnn.org", tf=70, cf=67, country="US", backlinks=4000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("bbc.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("cnn.org", tf=70, cf=67, country="US", backlinks=4000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("bbc.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("cnn.org", tf=70, cf=67, country="US", backlinks=4000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("bbc.co.uk", tf=99, cf=78, country="UK", backlinks=5000, ref_domains=3000))
            ref_domains.append(MajesticRefDomainStruct("cnn.org", tf=70, cf=67, country="US", backlinks=4000, ref_domains=3000))
            total_record = len(ref_domains)
            for ref_domain in ref_domains:
                if isinstance(ref_domain, MajesticRefDomainStruct):
                    if ref_domain.country in _bad_country:
                        bad_country_count += 1
                        if ref_domain.backlinks > max_backlinks_for_single_bad_country:
                            raise ValueError("{0:s} from bad country has more than {1:d} backlinks.".format(ref_domain.domain,max_backlinks_for_single_bad_country))

            bad_country_ratio = bad_country_count/total_record
            if total_record > 0 and bad_country_ratio > max_bad_country_ratio:
                raise ValueError("bad country ratio in ref domains is too high: {0:.1f} percent.".format(bad_country_ratio*100,))
            return True
        print(_filter_ref_domains("bbc.com"))

    def testAnchorText(self):
        self._spam_anchor = ["tit", "sex", "oral sex", "熟女"]

        def isOK(domain: str):
            min_anchor_variation_limit = 2
            no_follow_limit = 0.5
            domain_contain_limit = 5
            is_in_anchor = False
            temp_list = ["boot", "tistd", "bbc.co.uk", "ok", "美熟女", "中国", "afafa", "fafa"]
            #temp_list = ["boot", "tistd", "ok", "中国", "熟女s", "bbc.co.uk"]
            anchor_list, total, deleted, nofollow = (temp_list, 1000, 200, 100)  # change this
            if len(anchor_list) <= min_anchor_variation_limit:
                raise ValueError("number of anchor variation is less than 2.")
            elif (deleted + nofollow)/total > no_follow_limit:
                raise ValueError("deleted and nofollow backlinks are more than 50%.")
            elif len(self._spam_anchor) > 0:
                count = 0
                for anchor in anchor_list:
                    if domain in anchor and count < domain_contain_limit:
                        is_in_anchor = True

                    # if not MajesticFilter._is_valid_ISO8859_1_str(anchor):
                    #     raise ValueError("anchor contains invalid western language word: {0:s}.".format(anchor,))
                    for spam in self._spam_anchor:
                        # pattern = re.compile(spam, re.IGNORECASE)
                        # if re.search(pattern, anchor):
                        if spam in anchor:
                            raise ValueError("anchor {0:s} is in spam word {1:s}".format(anchor, spam))
                    count += 1

            if not is_in_anchor:
                raise ValueError("anchor does not have the domain name in top {0:d} results.".format(domain_contain_limit,))

            return True

        domain = "bbc.co.uk"
        print(isOK(domain))

    def testFilter(self):
        manager = AccountManager()
        manager.AccountList.append(majestic_account)
        input_param ={"input_queue": queue.Queue(), "output_queue": queue.Queue(), "stop_event": Event()}
        filter = MajesticFilter(manager=manager, **input_param)
        param = {"Account": majestic_account}
        links = FileIO.FileHandler.read_lines_from_file("/Users/superCat/Desktop/PycharmProjectPortable/test/spam_test1.txt")
        for link in links:
            site = FilteredDomainData(domain=link)
            filter.process_data(data=site, **param)

    def testSortList(self):
        anchorTextRows = []
        anchorTextRows.append(("tit", 10000, 2000, 1000))
        anchorTextRows.append(("man", 20000, 2000, 1000))
        anchorTextRows.append(("woman", 20000, 2000, 1000))
        anchorTextRows.append(("animal", 30000, 2000, 1000))
        anchorTexts = [x[0] for x in sorted(anchorTextRows, key=lambda anchorRow: anchorRow[1], reverse=True)]
        for anchor in anchorTexts:
            print(anchor)

    def testGetBacklinks(self):
        domain = "bufinserv.co.uk"
        max_count = 10
        niche = ""
        # niche = "Business/Financial Services"
        backlinks = majestic.get_backlinks(domain, max_count=max_count, topic=niche, is_dev=False)
        for item in backlinks:
            print(item)

    def testGetBackLinks2(self):
        logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/Gambling2.csv"
        FileHandler.create_file_if_not_exist(logging_path)
        Logging.CsvLogger.log_to_file_path(logging_path, [MajesticBacklinkDataStruct.get_tilte(), ])
        max_count = 100
        niche = "Games/Gambling"
        # niche = "Business/Financial Services"
        sites = GoogleCom.get_sites(keyword="gambling", index=0)
        backlinks = GoogleMajestic.get_sites_by_seed_sites(majestic, sites, catagories=niche, iteration=0, count_per_domain=max_count)
        for item in backlinks:
            if isinstance(item, MajesticBacklinkDataStruct):
                print(item)
                Logging.CsvLogger.log_to_file_path(logging_path, [item.to_tuple(), ])

    def testGetBackLinks3(self):
        file_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/GamblingSeed1.txt"
        sites = FileHandler.read_lines_from_file(file_path)
        logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/Gambling3.csv"
        FileHandler.create_file_if_not_exist(logging_path)
        # Logging.CsvLogger.log_to_file_path(logging_path, [MajesticBacklinkDataStruct.get_tilte(), ])
        max_count = 2000
        # niche = "Games/Gambling"
        # niche = "Business/Financial Services"
        niche = ""
        #sites = GoogleCom.get_sites(keyword="gambling", index=0)
        backlinks = GoogleMajestic.get_sites_by_seed_sites(majestic, sites, catagories=niche, iteration=0,
                                                           count_per_domain=max_count, callback=backlink_callback)
        # for item in backlinks:
        #     if isinstance(item, MajesticBacklinkDataStruct):
        #         print(item)
        #         Logging.CsvLogger.log_to_file_path(logging_path, [item.to_tuple(), ])

    def testCatagory(self):
        catagories = ["","Arts", "Arts/", "arts", "Arts/Movies", "Arts/Movie"]
        for item in catagories:
            try:
                print(CategoryManager.decode_sub_category(item))
            except Exception as ex:
                print(ex)

    def testCatagory2(self):
        import csv
        path = "/Users/superCat/Desktop/PycharmProjectPortable/test/17-09-2015-Good-Results.csv"
        counter = 0
        with open(path, mode='r', newline='') as csv_file:
            rd = csv.reader(csv_file, delimiter=',')
            for row in rd:
                if counter > 0:
                    parse_majestic_topic(row[10])

                counter += 1
                print("current loc:", counter)

    def testCategory3(self):
        save_path = "/Users/superCat/Desktop/PycharmProjectPortable/test/CategoryDB.db"
        manager = CategoryManager()
        db_manager = CategoryDBManager(save_path)
        for main_category in MainCategory.get_all_category():
            sub_categories = [SubCategory(main_category, item) for item in manager.get_sub_categories(main_category)]
            for item in sub_categories:
                db_manager.get_sub_category(item)
        db_manager.save()

        for item in db_manager.categories:
            if isinstance(item, Serializable):
                print(item.get_serializable(False))


    def testImportSeeds0(self):
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/NewCategorySeedDB.db"
        path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/Gambling3.csv"
        db = CategorySeedSiteDB(seed_db_addr)
        with open(path, mode='rt') as csv_file:
            # lines = len(csv_file.readlines())
            rd = csv.reader(csv_file, delimiter=',')
            header = next(rd) # skip header
            counter = 0
            temp = []
            while True:
                try:
                    row = next(rd)
                    if len(row) == 0:
                        break
                    if len(row) == 6:
                        domain, backlink, tf, cf, topic, topical_tf = row
                        print("current loc:", counter, "data:", row)
                        # if len(topic) > 0:
                        #     decoded_topic = basic_manager.decode_sub_category(topic, False)
                        data = MajesticBacklinkDataStruct(ref_domain=domain, src_cf=int(cf), src_tf=int(tf),
                                                          src_topical_tf=int(topical_tf))
                        temp.append(data)
                except StopIteration:
                    print('stop iteration')
                    break
                except Exception as ex:

                    print("exception:", str(ex), "row:", str(counter))
                    if len(str(ex)) == 0:
                        break
                finally:
                    counter += 1

        db.save_to_table('Games/Gambling', temp)
        db.close()

    def testImportSeeds(self):
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB.db"
        category_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/test/CategoryDB.db"
        db = CategorySeedSiteDB(seed_db_addr)
        basic_manager = CategoryManager()
        category_manager = CategoryDBManager(category_db_addr)
        seed_manager = CategorySiteDBManager(CategorySeedSiteDB, db_path=seed_db_addr)
        import csv
        path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/Gambling3.csv"
        counter = 0
        with open(path, mode='r', newline='', encoding='utf-8') as csv_file:
            # lines = len(csv_file.readlines())
            rd = csv.reader(csv_file, delimiter=',')
            for row in rd:
                try:
                    if len(row) == 6:
                        domain, backlink, tf, cf, topic, topical_tf = row
                        if len(topic) > 0:
                            decoded_topic = basic_manager.decode_sub_category(topic, False)
                            data = MajesticBacklinkDataStruct(ref_domain=domain, src_cf=int(cf),
                                                              src_tf=int(tf), src_topic=str(decoded_topic), src_topical_tf=int(topical_tf))
                            seed_manager.append_to_buff(data=data, category=str(decoded_topic))
                except Exception as ex:
                        print(ex, "row:", row)
                finally:
                    counter += 1
                    print("current loc:", counter, "data:", row)
        seed_manager.close()

    def test_possibility(self):
        import random
        zero_times = 0
        one_times = 0
        for i in range(1000):
            j = random.randint(0, 1)
            if j == 1:
                one_times += 1
            elif j == 0:
                zero_times += 1
        print("zero_times:", zero_times, "one_times:", one_times)

    def testGetSeedsFromRefDomains(self):
        import random
        logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/GeneralSeed4.csv"
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB_WithCountry.db"
        seed_manager = CategorySiteDBManager(CategorySeedSiteDB, db_path=seed_db_addr)  # was seed_db_addr
        thread_pool_size = 20
        max_count = 5000
        seed_manager._max_site_limit = int(thread_pool_size * max_count*0.75)

    def test_list(self):
        temp_sites = ["abc", "faa", "afa", "afa"]
        temp_sites = list(set(temp_sites))
        for item in temp_sites:
            print(item)

    def testGetSeedsFromBacklinks(self):
        import random
        import time
        logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/GeneralSeed5.csv"
        # seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB_WithCountry_Temp.db"
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB3.db"
        # logging_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/GeneralSeed4.csv"
        # seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB.db"
        save_seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB3.db"
        category_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/test/CategoryDB.db"
        seed_site_file_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/SiteFromResults.txt"
        db = CategorySeedSiteDB(seed_db_addr)
        basic_manager = CategoryManager()
        thread_pool_size = 20
        max_count = 5000

        category_manager = CategoryDBManager(category_db_addr)
        seed_manager = CategorySiteDBManager(CategorySeedSiteDB, db_path=save_seed_db_addr)  # was seed_db_addr
        seed_manager._max_site_limit = int(thread_pool_size * max_count*0.75)

        counter = 0
        country_file_path = "/Users/superCat/Desktop/PycharmProjectPortable/SpamFilter/bad_country.txt"
        bad_countries = [x.upper() for x in FileIO.FileHandler.read_lines_from_file(country_file_path)]

        def backlink_callback_inner(link_data):

            if isinstance(link_data, MajesticRefDomainStruct):
                if link_data.country in bad_countries or link_data.tf < 5 or link_data.tf > 95:
                    link_data = None
                    pass
                else:
                    link_data = MajesticBacklinkDataStruct(ref_domain=link_data.domain, backlink=link_data.domain,
                                                           src_tf=link_data.tf, src_cf=link_data.cf,
                                                           src_topic=link_data.src_topic,
                                                           src_topical_tf=link_data.src_topic_tf,
                                                           country_code=link_data.country, potential_url=link_data.potential_url)

            if isinstance(link_data, MajesticBacklinkDataStruct):
                if len(link_data.src_topic) > 1:
                    decoded_topic = basic_manager.decode_sub_category(link_data.src_topic, False)
                    # print(backlink)
                    Logging.CsvLogger.log_to_file_path(logging_path, [link_data.to_tuple(), ])
                    seed_manager.append_to_buff(data=link_data, category=str(decoded_topic))


        total_count = 0
        seed_init_limit = 400
        seed_depth_limit = 3000
        temp_niches = []
        niches = []

        for niche in temp_niches:  # make valid niche for seeds
            # if niche.endswith("General"):
            #     niches.append(niche.rstrip("General"))
            # else:
            niches.append(niche)

        forbidden_list = ["bbc.co.uk", "wikipedia.org", "youtube.com", "amazon.co.uk", "facebook.com", "google.com", ".ru", ".cn", ".jp"]
        for niche in niches:
            decoded_topic = basic_manager.decode_sub_category(niche, False)
            print(decoded_topic)
        minimum_tf = 25
        temp_sites = []
        target_ca = ["Society/Law", "Society/Politics", "Society/Issues", "Business/Financial Services", "Society/Government"]
        sites = []
        parameters = {"TF": minimum_tf}
        key_words = ["Alcohol law", "Banking law", "Antitrust law", "Aviation law", "Corporate law", "Communications law",
                     "Construction law", "Consumer law", "Drug control law", "Insurance law", "Tax law"]
        # for item in key_words:
        #     temp_sites += GoogleCom.get_sites(keyword=item, index=0, filter_list=forbidden_list, blog=True)[0:]
        #     print("sites count:", len(temp_sites))
        #     time.sleep(2)
        # temp_sites = FileHandler.read_lines_from_file(seed_site_file_path)
        # temp_sites = list(set(temp_sites))
        print("seeds total:", len(temp_sites))
        categories = db.get_sub_category_tables_name()
        for niche in niches:
            target_ca += [x for x in categories if niche in x]

        seed_count = 0
        load_limit = seed_init_limit*4

        def check_ending(domain: str):
            is_wrong_ending = False
            for item in forbidden_list:
                if domain.endswith(item):
                    is_wrong_ending = True
                    break
            return not is_wrong_ending

        for ca in target_ca:
            temp_sites += [y for y in filter(check_ending,
                                             [x.ref_domain for x in db.get_from_table(ca, 0, load_limit, parameters,
                                                                                      reverse_read=True,
                                                                                      random_read=True)])]

        db.close()


        seed_count = len(temp_sites)
        # seed_init_limit = seed_count  #---------------------------

        if seed_count <= seed_init_limit:
            sites = temp_sites
        elif seed_init_limit < seed_count <= seed_init_limit * 2:
            sites = temp_sites[::2]
        else:
            while len(sites) < seed_init_limit:
                site = temp_sites[random.randint(0, seed_count-1)]
                if site not in sites:
                    sites.append(site)
        # GoogleMajestic.get_sites_by_seed_sites(majestic, sites, catagories=niches, iteration=1,
        #                                                    count_per_domain=max_count, callback=backlink_callback_inner,
        #                                                    max_count=seed_depth_limit, tf=minimum_tf)
        GoogleMajestic.get_sites_by_seed_sites_muti_threads(majestic, sites, catagories=target_ca, iteration=4,
                                                           count_per_domain=max_count, callback=backlink_callback_inner,
                                                           max_count=seed_depth_limit + seed_init_limit,
                                                           thread_pool_size=thread_pool_size, tf=minimum_tf, get_backlinks=False, bad_country_list=bad_countries)
        seed_manager.close()
        # total_count += len(backlinks)
        # print("job finished, total backlinks:", total_count)

    def testPrintSeedDB(self):
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB3.db"
        log_file_path = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/SeedLog3.csv"
        enable_log = True
        FileHandler.remove_file_if_exist(log_file_path)
        db = CategorySeedSiteDB(seed_db_addr)
        # seed_manager = CategorySiteDBManager(CategorySeedSiteDB, db_path=seed_db_addr)
        categories = db.get_sub_category_tables_name()
        total_count = 0
        target_niche = ""
        parameters = {"TF": 0}
        if enable_log:
            CsvLogger.log_to_file_path(log_file_path, [("parameters", str(parameters)), ])
        # parameters = {"TF": 20}
        for item in categories:
            if target_niche in item or len(target_niche) == 0:
                count = db.get_total(item, **parameters)
                total_count += count
                print(item, "  ", count)
                if enable_log:
                    CsvLogger.log_to_file_path(log_file_path, [(item, str(count)), ])
        print("total:", total_count)
        if enable_log:
            CsvLogger.log_to_file_path(log_file_path, [("total", str(total_count)), ])

    def testPrintSeedDBSingleNiche(self):
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB.db"
        parameters = {"TF": 0}
        db = CategorySeedSiteDB(seed_db_addr)
        total = db.get_total("Society/Law", **parameters)
        db.close()
        print(total)

    def testeedExport(self):
        seed_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/sync/SeedSitesList"
        seed_db = SeedSiteDB("26/10/2015 Marketing CF20", db_addr=seed_db_addr)

        categoy_db_addr = "/Users/superCat/Desktop/PycharmProjectPortable/Seeds/CategorySeedDB.db"
        db = CategorySeedSiteDB(categoy_db_addr)
        # seed_manager = CategorySiteDBManager(CategorySeedSiteDB, db_path=categoy_db_addr)
        categories = db.get_sub_category_tables_name()
        target_ca = [x for x in categories if "Business/Marketing and Advertising" in x]
        sites = []
        seeds_needed = 20000
        percentage = 1
        parameters = {"CF": 20, }
        for ca in target_ca:
            sites.clear()
            count = db.get_total(ca)
            if percentage == 1 and count > seeds_needed:
                count = seeds_needed
            count = int(percentage * count)
            if count > 0:
                temp = db.get_from_table(ca, 0, count, random_read=False, filter_dict=parameters)
                for item in temp:
                    if isinstance(item, MajesticBacklinkDataStruct):
                        sites.append((item.ref_domain, 0))
                seed_db.add_sites(sites, skip_check=True)
        seed_db.close()



