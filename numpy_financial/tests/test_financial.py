
from decimal import Decimal

# Don't use 'import numpy as np', to avoid accidentally testing
# the versions in numpy instead of numpy_financial.
import numpy
from numpy.testing import (
    assert_, assert_almost_equal, assert_allclose, assert_equal, assert_raises
    )

import numpy_financial as npf
import pytest


class TestFinancial(object):
    def test_npv_irr_congruence(self):
        # IRR is defined as the rate required for the present value of a
        # a series of cashflows to be zero i.e. NPV(IRR(x), x) = 0
        cashflows = numpy.array([-40000, 5000, 8000, 12000, 30000])
        assert_allclose(npf.npv(npf.irr(cashflows), cashflows), 0,
                        atol=1e-10, rtol=0)

    def test_rate(self):
        assert_almost_equal(npf.rate(10, 0, -3500, 10000), 0.1107, 4)

    def test_rate_decimal(self):
        rate = npf.rate(Decimal('10'), Decimal('0'), Decimal('-3500'),
                        Decimal('10000'))
        assert_equal(Decimal('0.1106908537142689284704528100'), rate)

    def test_irr(self):
        v = [-150000, 15000, 25000, 35000, 45000, 60000]
        assert_almost_equal(npf.irr(v), 0.0524, 2)
        v = [-100, 0, 0, 74]
        assert_almost_equal(npf.irr(v), -0.0955, 2)
        v = [-100, 39, 59, 55, 20]
        assert_almost_equal(npf.irr(v), 0.28095, 2)
        v = [-100, 100, 0, -7]
        assert_almost_equal(npf.irr(v), -0.0833, 2)
        v = [-100, 100, 0, 7]
        assert_almost_equal(npf.irr(v), 0.06206, 2)
        v = [-5, 10.5, 1, -8, 1]
        assert_almost_equal(npf.irr(v), 0.0886, 2)

        # Test that if there is no solution then npf.irr returns nan
        # Fixes gh-6744
        v = [-1, -2, -3]
        assert_equal(npf.irr(v), numpy.nan)

    def test_pv(self):
        assert_almost_equal(npf.pv(0.07, 20, 12000, 0), -127128.17, 2)

    def test_pv_decimal(self):
        assert_equal(npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0')),
                     Decimal('-127128.1709461939327295222005'))

    def test_fv(self):
        assert_equal(npf.fv(0.075, 20, -2000, 0, 0), 86609.362673042924)

    def test_fv_decimal(self):
        assert_equal(npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            0, 0),
                     Decimal('86609.36267304300040536731624'))

    def test_pmt(self):
        res = npf.pmt(0.08 / 12, 5 * 12, 15000)
        tgt = -304.145914
        assert_allclose(res, tgt)
        # Test the edge case where rate == 0.0
        res = npf.pmt(0.0, 5 * 12, 15000)
        tgt = -250.0
        assert_allclose(res, tgt)
        # Test the case where we use broadcast and
        # the arguments passed in are arrays.
        res = npf.pmt([[0.0, 0.8], [0.3, 0.8]], [12, 3], [2000, 20000])
        tgt = numpy.array([[-166.66667, -19311.258], [-626.90814, -19311.258]])
        assert_allclose(res, tgt)

    def test_pmt_decimal(self):
        res = npf.pmt(Decimal('0.08') / Decimal('12'), 5 * 12, 15000)
        tgt = Decimal('-304.1459143262052370338701494')
        assert_equal(res, tgt)
        # Test the edge case where rate == 0.0
        res = npf.pmt(Decimal('0'), Decimal('60'), Decimal('15000'))
        tgt = -250
        assert_equal(res, tgt)

        # Test the case where we use broadcast and
        # the arguments passed in are arrays.
        res = npf.pmt([[Decimal('0'), Decimal('0.8')],
                       [Decimal('0.3'), Decimal('0.8')]],
                      [Decimal('12'), Decimal('3')],
                      [Decimal('2000'), Decimal('20000')])
        tgt = numpy.array([[Decimal('-166.6666666666666666666666667'),
                            Decimal('-19311.25827814569536423841060')],
                           [Decimal('-626.9081401700757748402586600'),
                            Decimal('-19311.25827814569536423841060')]])

        # Cannot use the `assert_allclose` because it uses isfinite under
        # the covers which does not support the Decimal type
        # See issue: https://github.com/numpy/numpy/issues/9954
        assert_equal(res[0][0], tgt[0][0])
        assert_equal(res[0][1], tgt[0][1])
        assert_equal(res[1][0], tgt[1][0])
        assert_equal(res[1][1], tgt[1][1])

    def test_ppmt(self):
        assert_equal(numpy.round(npf.ppmt(0.1 / 12, 1, 60, 55000), 2), -710.25)

    def test_ppmt_decimal(self):
        assert_equal(npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000')),
                     Decimal('-710.2541257864217612489830917'))

    # Two tests showing how Decimal is actually getting at a more exact result
    # .23 / 12 does not come out nicely as a float but does as a decimal
    def test_ppmt_special_rate(self):
        assert_equal(numpy.round(npf.ppmt(0.23 / 12, 1, 60, 10000000000), 8),
                     -90238044.232277036)

    def test_ppmt_special_rate_decimal(self):
        # When rounded out to 8 decimal places like the float based test,
        # this should not equal the same value as the float, substituted
        # for the decimal
        def raise_error_because_not_equal():
            assert_equal(
                round(npf.ppmt(Decimal('0.23') / Decimal('12'), 1, 60,
                               Decimal('10000000000')), 8),
                Decimal('-90238044.232277036'))

        assert_raises(AssertionError, raise_error_because_not_equal)
        assert_equal(npf.ppmt(Decimal('0.23') / Decimal('12'), 1, 60,
                              Decimal('10000000000')),
                     Decimal('-90238044.2322778884413969909'))

    def test_ipmt(self):
        assert_almost_equal(numpy.round(npf.ipmt(0.1 / 12, 1, 24, 2000), 2),
                            -16.67)

    def test_ipmt_decimal(self):
        result = npf.ipmt(Decimal('0.1') / Decimal('12'), 1, 24, 2000)
        assert_equal(result.flat[0], Decimal('-16.66666666666666666666666667'))

    def test_nper(self):
        assert_almost_equal(npf.nper(0.075, -2000, 0, 100000.),
                            21.54, 2)

    def test_nper2(self):
        assert_almost_equal(npf.nper(0.0, -2000, 0, 100000.),
                            50.0, 1)

    def test_npv(self):
        assert_almost_equal(
            npf.npv(0.05, [-15000, 1500, 2500, 3500, 4500, 6000]),
            122.89, 2)

    def test_npv_decimal(self):
        assert_equal(
            npf.npv(Decimal('0.05'), [-15000, 1500, 2500, 3500, 4500, 6000]),
            Decimal('122.894854950942692161628715'))

    def test_mirr(self):
        val = [-4500, -800, 800, 800, 600, 600, 800, 800, 700, 3000]
        assert_almost_equal(npf.mirr(val, 0.08, 0.055), 0.0666, 4)

        val = [-120000, 39000, 30000, 21000, 37000, 46000]
        assert_almost_equal(npf.mirr(val, 0.10, 0.12), 0.126094, 6)

        val = [100, 200, -50, 300, -200]
        assert_almost_equal(npf.mirr(val, 0.05, 0.06), 0.3428, 4)

        val = [39000, 30000, 21000, 37000, 46000]
        assert_(numpy.isnan(npf.mirr(val, 0.10, 0.12)))

    def test_mirr_decimal(self):
        val = [Decimal('-4500'), Decimal('-800'), Decimal('800'),
               Decimal('800'), Decimal('600'), Decimal('600'), Decimal('800'),
               Decimal('800'), Decimal('700'), Decimal('3000')]
        assert_equal(npf.mirr(val, Decimal('0.08'), Decimal('0.055')),
                     Decimal('0.066597175031553548874239618'))

        val = [Decimal('-120000'), Decimal('39000'), Decimal('30000'),
               Decimal('21000'), Decimal('37000'), Decimal('46000')]
        assert_equal(npf.mirr(val, Decimal('0.10'), Decimal('0.12')),
                     Decimal('0.126094130365905145828421880'))

        val = [Decimal('100'), Decimal('200'), Decimal('-50'),
               Decimal('300'), Decimal('-200')]
        assert_equal(npf.mirr(val, Decimal('0.05'), Decimal('0.06')),
                     Decimal('0.342823387842176663647819868'))

        val = [Decimal('39000'), Decimal('30000'), Decimal('21000'),
               Decimal('37000'), Decimal('46000')]
        assert_(numpy.isnan(npf.mirr(val, Decimal('0.10'), Decimal('0.12'))))

    def test_when(self):
        # begin
        assert_equal(npf.rate(10, 20, -3500, 10000, 1),
                     npf.rate(10, 20, -3500, 10000, 'begin'))
        # end
        assert_equal(npf.rate(10, 20, -3500, 10000),
                     npf.rate(10, 20, -3500, 10000, 'end'))
        assert_equal(npf.rate(10, 20, -3500, 10000, 0),
                     npf.rate(10, 20, -3500, 10000, 'end'))

        # begin
        assert_equal(npf.pv(0.07, 20, 12000, 0, 1),
                     npf.pv(0.07, 20, 12000, 0, 'begin'))
        # end
        assert_equal(npf.pv(0.07, 20, 12000, 0),
                     npf.pv(0.07, 20, 12000, 0, 'end'))
        assert_equal(npf.pv(0.07, 20, 12000, 0, 0),
                     npf.pv(0.07, 20, 12000, 0, 'end'))

        # begin
        assert_equal(npf.fv(0.075, 20, -2000, 0, 1),
                     npf.fv(0.075, 20, -2000, 0, 'begin'))
        # end
        assert_equal(npf.fv(0.075, 20, -2000, 0),
                     npf.fv(0.075, 20, -2000, 0, 'end'))
        assert_equal(npf.fv(0.075, 20, -2000, 0, 0),
                     npf.fv(0.075, 20, -2000, 0, 'end'))

        # begin
        assert_equal(npf.pmt(0.08 / 12, 5 * 12, 15000., 0, 1),
                     npf.pmt(0.08 / 12, 5 * 12, 15000., 0, 'begin'))
        # end
        assert_equal(npf.pmt(0.08 / 12, 5 * 12, 15000., 0),
                     npf.pmt(0.08 / 12, 5 * 12, 15000., 0, 'end'))
        assert_equal(npf.pmt(0.08 / 12, 5 * 12, 15000., 0, 0),
                     npf.pmt(0.08 / 12, 5 * 12, 15000., 0, 'end'))

        # begin
        assert_equal(npf.ppmt(0.1 / 12, 1, 60, 55000, 0, 1),
                     npf.ppmt(0.1 / 12, 1, 60, 55000, 0, 'begin'))
        # end
        assert_equal(npf.ppmt(0.1 / 12, 1, 60, 55000, 0),
                     npf.ppmt(0.1 / 12, 1, 60, 55000, 0, 'end'))
        assert_equal(npf.ppmt(0.1 / 12, 1, 60, 55000, 0, 0),
                     npf.ppmt(0.1 / 12, 1, 60, 55000, 0, 'end'))

        # begin
        assert_equal(npf.ipmt(0.1 / 12, 1, 24, 2000, 0, 1),
                     npf.ipmt(0.1 / 12, 1, 24, 2000, 0, 'begin'))
        # end
        assert_equal(npf.ipmt(0.1 / 12, 1, 24, 2000, 0),
                     npf.ipmt(0.1 / 12, 1, 24, 2000, 0, 'end'))
        assert_equal(npf.ipmt(0.1 / 12, 1, 24, 2000, 0, 0),
                     npf.ipmt(0.1 / 12, 1, 24, 2000, 0, 'end'))

        # begin
        assert_equal(npf.nper(0.075, -2000, 0, 100000., 1),
                     npf.nper(0.075, -2000, 0, 100000., 'begin'))
        # end
        assert_equal(npf.nper(0.075, -2000, 0, 100000.),
                     npf.nper(0.075, -2000, 0, 100000., 'end'))
        assert_equal(npf.nper(0.075, -2000, 0, 100000., 0),
                     npf.nper(0.075, -2000, 0, 100000., 'end'))

    def test_decimal_with_when(self):
        """
        Test that decimals are still supported if the when argument is passed
        """
        # begin
        assert_equal(npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000'), Decimal('1')),
                     npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000'), 'begin'))
        # end
        assert_equal(npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000')),
                     npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000'), 'end'))
        assert_equal(npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000'), Decimal('0')),
                     npf.rate(Decimal('10'), Decimal('20'), Decimal('-3500'),
                              Decimal('10000'), 'end'))

        # begin
        assert_equal(npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0'), Decimal('1')),
                     npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0'), 'begin'))
        # end
        assert_equal(npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0')),
                     npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0'), 'end'))
        assert_equal(npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0'), Decimal('0')),
                     npf.pv(Decimal('0.07'), Decimal('20'), Decimal('12000'),
                            Decimal('0'), 'end'))

        # begin
        assert_equal(npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0'), Decimal('1')),
                     npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0'), 'begin'))
        # end
        assert_equal(npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0')),
                     npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0'), 'end'))
        assert_equal(npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0'), Decimal('0')),
                     npf.fv(Decimal('0.075'), Decimal('20'), Decimal('-2000'),
                            Decimal('0'), 'end'))

        # begin
        assert_equal(npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0'), Decimal('1')),
                     npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0'), 'begin'))
        # end
        assert_equal(npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0')),
                     npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0'), 'end'))
        assert_equal(npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0'), Decimal('0')),
                     npf.pmt(Decimal('0.08') / Decimal('12'),
                             Decimal('5') * Decimal('12'), Decimal('15000.'),
                             Decimal('0'), 'end'))

        # begin
        assert_equal(npf.ppmt(Decimal('0.1') / Decimal('12'),
                              Decimal('1'), Decimal('60'), Decimal('55000'),
                              Decimal('0'), Decimal('1')),
                     npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000'),
                              Decimal('0'), 'begin'))
        # end
        assert_equal(npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000'), Decimal('0')),
                     npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000'), Decimal('0'),
                              'end'))
        assert_equal(npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000'), Decimal('0'),
                              Decimal('0')),
                     npf.ppmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('60'), Decimal('55000'), Decimal('0'),
                              'end'))

        # begin
        assert_equal(npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0'), Decimal('1')).flat[0],
                     npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0'), 'begin').flat[0])
        # end
        assert_equal(npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0')).flat[0],
                     npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0'), 'end').flat[0])
        assert_equal(npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0'), Decimal('0')).flat[0],
                     npf.ipmt(Decimal('0.1') / Decimal('12'), Decimal('1'),
                              Decimal('24'), Decimal('2000'),
                              Decimal('0'), 'end').flat[0])

    def test_broadcast(self):
        assert_almost_equal(npf.nper(0.075, -2000, 0, 100000., [0, 1]),
                            [21.5449442, 20.76156441], 4)

        assert_almost_equal(npf.ipmt(0.1 / 12, list(range(5)), 24, 2000),
                            [-17.29165168, -16.66666667, -16.03647345,
                             -15.40102862, -14.76028842], 4)

        assert_almost_equal(npf.ppmt(0.1 / 12, list(range(5)), 24, 2000),
                            [-74.998201, -75.62318601, -76.25337923,
                             -76.88882405, -77.52956425], 4)

        assert_almost_equal(npf.ppmt(0.1 / 12, list(range(5)), 24, 2000, 0,
                                     [0, 0, 1, 'end', 'begin']),
                            [-74.998201, -75.62318601, -75.62318601,
                             -76.88882405, -76.88882405], 4)

    def test_broadcast_decimal(self):
        # Use almost equal because precision is tested in the explicit tests,
        # this test is to ensure broadcast with Decimal is not broken.
        assert_almost_equal(npf.ipmt(Decimal('0.1') / Decimal('12'),
                                     list(range(5)), Decimal('24'),
                                     Decimal('2000')),
                            [Decimal('-17.29165168'), Decimal('-16.66666667'),
                             Decimal('-16.03647345'), Decimal('-15.40102862'),
                             Decimal('-14.76028842')], 4)

        assert_almost_equal(npf.ppmt(Decimal('0.1') / Decimal('12'),
                                     list(range(5)), Decimal('24'),
                                     Decimal('2000')),
                            [Decimal('-74.998201'), Decimal('-75.62318601'),
                             Decimal('-76.25337923'), Decimal('-76.88882405'),
                             Decimal('-77.52956425')], 4)

        result = npf.ppmt(
            Decimal('0.1') / Decimal('12'),
            list(range(1, 5)),
            Decimal('24'),
            Decimal('2000'),
            Decimal('0'),
            [Decimal('0'), Decimal('1'), 'end', 'begin']
        )
        desired = [
            Decimal('-75.62318601'),
            Decimal('-75.62318601'),
            Decimal('-76.88882405'),
            Decimal('-76.88882405')
        ]
        assert_almost_equal(result, desired, decimal=4)


class TestNper:
    def test_basic_values(self):
        assert_allclose(
            npf.nper([0, 0.075], -2000, 0, 100000),
            [50, 21.544944],  # Computed using Google Sheet's NPER
            rtol=1e-5,
        )

    def test_gh_18(self):
        with numpy.errstate(divide='raise'):
            assert_allclose(
                npf.nper(0.1, 0, -500, 1500),
                11.52670461,  # Computed using Google Sheet's NPER
            )

    def test_infinite_payments(self):
        with numpy.errstate(divide='raise'):
            result = npf.nper(0, -0.0, 1000)
        assert_(result == numpy.inf)

    def test_no_interest(self):
        assert_(npf.nper(0, -100, 1000) == 10)


class TestIpmt:
    def test_float(self):
        assert_allclose(
            npf.ipmt(0.1 / 12, 1, 24, 2000),
            -16.666667,  # Computed using Google Sheet's IPMT
            rtol=1e-6,
        )

    def test_decimal(self):
        result = npf.ipmt(Decimal('0.1') / Decimal('12'), 1, 24, 2000)
        assert result == Decimal('-16.66666666666666666666666667')

    @pytest.mark.parametrize('when', [1, 'begin'])
    def test_when_is_begin(self, when):
        assert npf.ipmt(0.1 / 12, 1, 24, 2000, 0, when) == 0

    @pytest.mark.parametrize('when', [None, 0, 'end'])
    def test_when_is_end(self, when):
        if when is None:
            result = npf.ipmt(0.1 / 12, 1, 24, 2000)
        else:
            result = npf.ipmt(0.1 / 12, 1, 24, 2000, 0, when)
        assert_allclose(result, -16.666667, rtol=1e-6)

    @pytest.mark.parametrize('per, desired', [
        (0, numpy.nan),
        (1, 0),
        (2, -594.107158),
        (3, -592.971592),
    ])
    def test_gh_17(self, per, desired):
        # All desired results computed using Google Sheet's IPMT
        rate = 0.001988079518355057
        result = npf.ipmt(rate, per, 360, 300000, when="begin")
        if numpy.isnan(desired):
            assert numpy.isnan(result)
        else:
            assert_allclose(result, desired, rtol=1e-6)

    def test_broadcasting(self):
        desired = [
            numpy.nan,
            -16.66666667,
            -16.03647345,
            -15.40102862,
            -14.76028842
        ]
        assert_allclose(
            npf.ipmt(0.1 / 12, numpy.arange(5), 24, 2000),
            desired,
            rtol=1e-6,
        )

    def test_decimal_broadcasting(self):
        desired = [
            Decimal('-16.66666667'),
            Decimal('-16.03647345'),
            Decimal('-15.40102862'),
            Decimal('-14.76028842')
        ]
        result = npf.ipmt(
            Decimal('0.1') / Decimal('12'),
            list(range(1, 5)),
            Decimal('24'),
            Decimal('2000')
        )
        assert_almost_equal(result, desired, decimal=4)
