from collections import Counter
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


class ChartService:
    @staticmethod
    def build_break_distribution_figure(test_data: dict) -> Figure:
        """
        Build a Matplotlib Figure showing the distribution of 'Break' elements
        by Force Setting (N) and Failure Location.
        """
        elements = test_data.get("elements", [])
        broken_elements = [
            el for el in elements
            if str(el.get("result", "")).strip().lower() == "break"
        ]

        if not broken_elements:
            raise ValueError("There are no 'Break' samples in this test batch to plot distribution.")

        info = test_data.get("test_info", {})
        charge_no = info.get("charge_no", "")
        element_type = info.get("element_type", "")

        # 1. Group broken samples by Force Setting (N)
        force_counts = Counter()
        for el in broken_elements:
            try:
                f_val = int(float(el.get("setting_N", 0)))
            except ValueError:
                f_val = 0
            force_counts[f_val] += 1

        sorted_forces = sorted(force_counts.keys())
        # Remove redundant 'N' on each tick since X-axis label already states 'Setting Force (N)'
        force_labels = [str(f) for f in sorted_forces]
        force_values = [force_counts[f] for f in sorted_forces]

        # 2. Group broken samples by Failure Location / Mode
        failure_counts = Counter(
            (str(el.get("failure", "")).strip() or "Unspecified")
            for el in broken_elements
        )
        failure_labels = list(failure_counts.keys())
        failure_values = list(failure_counts.values())

        # Build Figure
        fig = Figure(figsize=(8.5, 4.0), dpi=100)

        # Subplot 1: Break count by Force Setting (N)
        ax1 = fig.add_subplot(121)
        bars1 = ax1.bar(force_labels, force_values, color="#d9534f", width=0.45, edgecolor="#a94442")
        ax1.set_title("Break Distribution by Force Setting (N)", fontsize=10, fontweight="bold")
        ax1.set_xlabel("Setting Force (N)", fontsize=9)
        ax1.set_ylabel("Broken Count", fontsize=9)
        ax1.set_ylim(0, max(force_values) * 1.2 + 0.5)  # Add ~20% top padding so labels never touch the top border
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.grid(axis="y", linestyle="--", alpha=0.5)
        for bar in bars1:
            h = bar.get_height()
            ax1.annotate(
                f"{h}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold"
            )

        # Subplot 2: Break count by Failure Location
        ax2 = fig.add_subplot(122)
        bars2 = ax2.bar(failure_labels, failure_values, color="#f0ad4e", width=0.35, edgecolor="#c08020")
        ax2.set_title("Break Distribution by Failure Location", fontsize=10, fontweight="bold")
        ax2.set_xlabel("Failure Type / Position", fontsize=9)
        ax2.set_ylabel("Broken Count", fontsize=9)
        ax2.set_ylim(0, max(failure_values) * 1.2 + 0.5)  # Add ~20% top padding for numbers like 10, 15, 20
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        for bar in bars2:
            h = bar.get_height()
            ax2.annotate(
                f"{h}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold"
            )

        fig.suptitle(
            f"Break Distribution — Charge: {charge_no} | Type: {element_type} | Breaks: {len(broken_elements)}/{len(elements)}",
            fontsize=11,
            fontweight="bold"
        )
        fig.tight_layout(rect=[0, 0.02, 1, 0.92])
        return fig