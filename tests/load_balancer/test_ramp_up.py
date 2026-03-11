"""Unit tests for apply_ramp_up_limit.

Covers: increase allowed after cooldown, increase blocked within cooldown,
decrease always allowed, no prior reduction allows increase, exact boundary,
zero cooldown disables hold, stepped ramp-up with step_a.
"""

from custom_components.ev_lb.load_balancer import apply_ramp_up_limit


class TestApplyRampUpLimit:
    """Tests for the ramp-up cooldown function."""

    def test_increase_allowed_after_cooldown(self):
        """Charger current can increase once the ramp-up cooldown has fully elapsed."""
        last_reduction = 1000.0
        now = 1031.0  # 31 s later > 30 s cooldown
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=last_reduction,
            now=now,
            ramp_up_time_s=30.0,
        )
        assert result == 16.0

    def test_increase_blocked_within_cooldown(self):
        """Charger current is held at its previous value while the ramp-up cooldown is still running."""
        last_reduction = 1000.0
        now = 1020.0  # only 20 s later < 30 s cooldown
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=last_reduction,
            now=now,
            ramp_up_time_s=30.0,
        )
        assert result == 10.0

    def test_decrease_always_allowed(self):
        """Current reductions are always applied immediately, regardless of the ramp-up cooldown."""
        last_reduction = 1000.0
        now = 1001.0  # only 1 s — well within cooldown
        result = apply_ramp_up_limit(
            prev_a=16.0,
            target_a=10.0,
            last_reduction_time=last_reduction,
            now=now,
            ramp_up_time_s=30.0,
        )
        assert result == 10.0

    def test_no_prior_reduction_increase_allowed(self):
        """On first start (no prior reduction recorded) the charger current can increase freely."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=None,
            now=1000.0,
            ramp_up_time_s=30.0,
        )
        assert result == 16.0

    def test_same_target_as_prev(self):
        """Holding at the same current level is always allowed (no change, no cooldown applies)."""
        result = apply_ramp_up_limit(
            prev_a=16.0,
            target_a=16.0,
            last_reduction_time=1000.0,
            now=1005.0,
            ramp_up_time_s=30.0,
        )
        assert result == 16.0

    def test_exactly_at_cooldown_boundary(self):
        """Charger current is allowed to increase at exactly the cooldown boundary (boundary is inclusive)."""
        last_reduction = 1000.0
        now = 1030.0  # exactly 30 s elapsed
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=last_reduction,
            now=now,
            ramp_up_time_s=30.0,
        )
        assert result == 16.0

    def test_zero_cooldown_always_allows_increase(self):
        """Setting ramp-up time to 0 disables the cooldown and allows instant current increases."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=1000.0,
            now=1000.0,  # zero elapsed
            ramp_up_time_s=0.0,
        )
        assert result == 16.0


class TestApplyRampUpLimitStepped:
    """Tests for the stepped ramp-up behaviour introduced by the step_a parameter.

    When step_a > 0, each cooldown expiry allows the current to increase by at
    most step_a toward the target (a "false target"), rather than jumping
    directly to the full headroom.  The caller is responsible for restarting
    the cooldown after each partial step.
    """

    def test_step_a_limits_increase_to_one_step(self):
        """After cooldown, current increases by exactly step_a when target exceeds prev + step_a."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=25.0,
            last_reduction_time=1000.0,
            now=1031.0,  # 31 s > 30 s cooldown
            ramp_up_time_s=30.0,
            step_a=8.0,
        )
        assert result == 18.0  # 10 + 8 = 18, not the full 25

    def test_step_a_capped_at_target(self):
        """When step_a would overshoot target, the result is capped at target_a."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=16.0,
            last_reduction_time=1000.0,
            now=1031.0,
            ramp_up_time_s=30.0,
            step_a=20.0,  # step_a > (target - prev)
        )
        assert result == 16.0  # capped at target, not 10 + 20 = 30

    def test_step_a_zero_behaves_like_default(self):
        """step_a=0 (default) preserves the original one-shot behaviour — full target on expiry."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=25.0,
            last_reduction_time=1000.0,
            now=1031.0,
            ramp_up_time_s=30.0,
            step_a=0.0,
        )
        assert result == 25.0  # no stepping — original behaviour

    def test_step_a_blocked_during_cooldown(self):
        """Step is not taken while the cooldown is still active, regardless of step_a."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=25.0,
            last_reduction_time=1000.0,
            now=1020.0,  # 20 s < 30 s cooldown
            ramp_up_time_s=30.0,
            step_a=8.0,
        )
        assert result == 10.0  # held — cooldown not elapsed

    def test_step_a_decrease_still_immediate(self):
        """A step_a value does not delay reductions — decreases are always instant."""
        result = apply_ramp_up_limit(
            prev_a=20.0,
            target_a=10.0,
            last_reduction_time=1000.0,
            now=1001.0,  # well within cooldown
            ramp_up_time_s=30.0,
            step_a=5.0,
        )
        assert result == 10.0  # instant reduction, step_a irrelevant

    def test_step_a_no_prior_reduction_free_increase(self):
        """step_a is irrelevant when no prior reduction has been recorded."""
        result = apply_ramp_up_limit(
            prev_a=10.0,
            target_a=25.0,
            last_reduction_time=None,
            now=1000.0,
            ramp_up_time_s=30.0,
            step_a=5.0,
        )
        assert result == 25.0  # no cooldown active → free increase ignoring step_a
