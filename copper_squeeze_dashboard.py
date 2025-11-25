import plotly.graph_objects as go
from plotly.subplots import make_subplots
from copper_indicators import CopperIndicators
import pandas as pd

class CopperSqueezeMonitor:
    def __init__(self):
        self.ind = CopperIndicators()
        self._copy_data_attributes()
        self.update()

    def _copy_data_attributes(self):
        for name in ['lme', 'inv', 'cftc', 'basis']:
            setattr(self, name, getattr(self.ind, name))

    def update(self):
        self.data = self.ind.get_all()
        
        # Raw percentiles
        bck  = self.data['backwardation_pct']
        inv  = self.data['inventory_tightness']
        cftc = self.data['cftc_pct']
        basis_raw = self.data['basis_pct']          # ← raw percentile (e.g. 25th)
    
        # Binary bonus: 25 pts only if basis >90th percentile
        basis_bonus = 25.0 if basis_raw >= 90.0 else 0.0
    
        self.composite = bck + inv + cftc + basis_bonus
        self.basis_bonus_applied = basis_bonus      # ← for display

    def get_verdict(self):
        c = self.composite
        if c < 150:  return "Low risk", "green"
        elif c < 200: return "Elevated risk", "yellow"
        elif c < 250: return "High squeeze risk", "orange"
        else:         return "Extreme squeeze risk", "red"
    
    def show_dashboard(self):
        self.update()
        d = self.data
        verdict, color = self.get_verdict()
    
        fig = go.Figure()
    
        labels = ["Backwardation", "Inventory Tightness", "CFTC Net Shorts", "COMEX-LME Basis"]
        raw_values = [d['backwardation_pct'], d['inventory_tightness'], d['cftc_pct'], d['basis_pct']]
        display_values = [d['backwardation_pct'], d['inventory_tightness'], d['cftc_pct'], self.basis_bonus_applied]
    
        colors = ["#2ca02c" if v<50 else "#ff7f0e" if v<75 else "#d62728" if v<90 else "#8B0000" for v in raw_values]
    
        texts = [f"{v:.1f}th" for v in raw_values]
        texts[3] = f"{d['basis_pct']:.1f}th → {self.basis_bonus_applied:.0f}/25 bonus"
    
        fig.add_trace(go.Bar(
            y=labels,
            x=display_values,
            orientation='h',
            marker_color=colors,
            text=texts,
            textposition="inside",
            textfont_size=14,
        ))
    
        fig.update_layout(
            title=f"<b>LME Copper Short-Squeeze Monitor</b><br>"
                  f"<span style='color:{color};font-size:20px'>{verdict.upper()} — {self.composite:.1f}/325</span>",
            title_x=0.5,
            xaxis=dict(range=[0,100], title="Score (higher = more extreme)"),
            yaxis=dict(autorange="reversed"),
            height=420,
            plot_bgcolor="white",
        )
        fig.show()

    # Individual Plots 
    def plot_backwardation(self):
        s = (self.lme['cash'] - self.lme['three_month']) / self.lme['three_month'] * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s.index, y=s, mode='lines', name='Backwardation %'))
        fig.add_scatter(x=[s.index[-1]], y=[s.iloc[-1]], mode='markers', marker=dict(color='red', size=10))
        fig.add_annotation(x="2025-06-23", y=4.08, text="Jun 2025: +4.08%", showarrow=True, arrowhead=2)
        fig.update_layout(title="LME Cash vs 3M Backwardation", height=520, template = 'plotly_white', yaxis_title = "Backwardation %")
        fig.show()

    def plot_inventory(self):
        s = self.inv['visible_inv'] / 1000
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=s.index, y=s, mode='lines',
            name='LME + COMEX (kt)', line=dict(color='#1f77b4', width=2)
        ))
        fig.add_scatter(
            x=[s.index[-1]], y=[s.iloc[-1]],
            mode='markers', marker=dict(color='red', size=12), name='Today'
        )
    
        fig.add_annotation(
            x=pd.to_datetime("2018-03-15"),
            y=587,
            text="Mar 2018: Historical high ~587kt (glut era)",
            showarrow=True, arrowhead=2, arrowcolor="gray",
            ax=50, ay=-50, bgcolor="lightgray", bordercolor="gray", borderwidth=1
        )
    
        fig.update_layout(
            title="Visible Inventory (LME + COMEX) — Western Deliverable Stocks",
            height=520, template="plotly_white",
            yaxis_title="Visible Inventory (In Thousand Tonnes)"
        )
        fig.show()

    def plot_cftc(self):
        s = self.cftc['Net_Shorts'] / 1000
        fig = go.Figure(go.Scatter(x=s.index, y=s, mode='lines', name='Net Short (k contracts)'))
        fig.add_scatter(x=[s.index[-1]], y=[s.iloc[-1]], mode='markers', marker_color='red', marker_size=10)
        fig.add_annotation(x="2017-08-15", y=83, text="Aug 2017 record", showarrow=True)
        fig.update_layout(title="CFTC Speculative Net Shorts", height=520, template = "plotly_white", yaxis_title = "Net Shorts (In Thousands)")
        fig.show()

    def plot_basis(self):
        s = self.basis['Basis_USD_t']
        fig = go.Figure(go.Scatter(x=s.index, y=s, mode='lines', name='COMEX − LME ($/t)'))
        fig.add_scatter(x=[s.index[-1]], y=[s.iloc[-1]], mode='markers', marker_color='red', marker_size=10)
        fig.add_annotation(x="2025-07-25", y=2866, text="Jul 2025: +$2,866", showarrow=True)
        fig.update_layout(title="COMEX-LME Daily Basis Spread", height=520, template = "plotly_white", yaxis_title = "Daily Basis Spread ($/t)")
        fig.show()