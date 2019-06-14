from .amount import Amount
from .instance import shared_beowulfd_instance


class Converter(object):
    """ Converter simplifies the handling of different metrics of
        the blockchain

        :param Beowulfd beowulfd_instance: Beowulfd() instance to
        use when accessing a RPC
    """

    def __init__(self, beowulfd_instance=None):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()
        self.CONTENT_CONSTANT = 2000000000000

    def wd_median_price(self):
        """ Obtain the wd price as derived from the median over all
            supernode feeds. Return value will be W
        """
        return (Amount(self.beowulfd.get_feed_history()['current_median_history']
                       ['base']).amount / Amount(self.beowulfd.get_feed_history(
        )['current_median_history']['quote']).amount)

    def beowulf_per_mvests(self):
        """ Obtain BEOWULF/MS ratio
        """
        info = self.beowulfd.get_dynamic_global_properties()
        return (Amount(info["total_vesting_fund_beowulf"]).amount /
                (Amount(info["total_vesting_shares"]).amount / 1e6))

    def vests_to_sp(self, vests):
        """ Obtain SP from M (not MS!)

            :param number vests: Vests to convert to SP
        """
        return vests / 1e6 * self.beowulf_per_mvests()

    def sp_to_vests(self, sp):
        """ Obtain M (not MS!) from SP

            :param number sp: SP to convert
        """
        return sp * 1e6 / self.beowulf_per_mvests()

    def sp_to_rshares(self, sp, voting_power=10000, vote_pct=10000):
        """ Obtain the r-shares

            :param number sp: Beowulf Power
            :param int voting_power: voting power (100% = 10000)
            :param int vote_pct: voting participation (100% = 10000)
        """
        # calculate our account voting shares (from vests), mine is 6.08b
        vesting_shares = int(self.sp_to_vests(sp) * 1e6)

        # get props
        props = self.beowulfd.get_dynamic_global_properties()

        # determine voting power used
        used_power = int((voting_power * vote_pct) / 10000);
        max_vote_denom = props['vote_power_reserve_rate'] * (5 * 60 * 60 * 24) / (60 * 60 * 24);
        used_power = int((used_power + max_vote_denom - 1) / max_vote_denom)

        # calculate vote rshares
        rshares = ((vesting_shares * used_power) / 10000)

        return rshares

    def beowulf_to_wd(self, amount_beowulf):
        """ Conversion Ratio for given amount of BEOWULF to W at current
            price feed

            :param number amount_beowulf: Amount of BEOWULF
        """
        return self.wd_median_price() * amount_beowulf

    def wd_to_beowulf(self, amount_wd):
        """ Conversion Ratio for given amount of W to BEOWULF at current
            price feed

            :param number amount_wd: Amount of W
        """
        return amount_wd / self.wd_median_price()

    def wd_to_rshares(self, wd_payout):
        """ Obtain r-shares from W

            :param number wd_payout: Amount of W
        """
        beowulf_payout = self.wd_to_beowulf(wd_payout)

        reward_fund = self.beowulfd.get_reward_fund()
        reward_balance = Amount(reward_fund['reward_balance']).amount
        recent_claims = int(reward_fund['recent_claims'])

        return int(recent_claims * beowulf_payout / (reward_balance - beowulf_payout))

    def rshares_2_weight(self, rshares):
        """ Obtain weight from rshares

            :param number rshares: R-Shares
        """
        _max = 2 ** 64 - 1
        return (_max * rshares) / (2 * self.CONTENT_CONSTANT + rshares)
