import pandas as pd
import hashlib
import plotly.express as px
import dash
from dash import html, dcc

# ---- Data loading & preprocessing ----
# Adjust the path if your CSV is in another folder
df = pd.read_csv("athlete_events.csv")

# Fill missing numeric values with median
df = df.fillna({
    "Age": df["Age"].median(),
    "Height": df["Height"].median(),
    "Weight": df["Weight"].median(),
})

# Optimise some dtypes (optional)
df = df.astype({
    "Age": "uint8",
    "Height": "uint8",
    "Weight": "uint8",
    "ID": "uint32",
    "Year": "int16",
})

# Anonymise names with SHA-256
df["Name"] = df["Name"].apply(
    lambda x: hashlib.sha256(str(x).encode()).hexdigest()
)

# Replace missing medals with explicit "None"
df["Medal"] = df["Medal"].fillna("None")

# Filter Italy (ITA)
ita = df[df["NOC"] == "ITA"].copy()

# ---- Figures: Italy overall ----

# 1) Top 10 sports where Italy has the most medals
ita_medals_unique = (
    ita[ita["Medal"] != "None"]
    .drop_duplicates(subset=["Games", "Event", "Medal"])
)

medals_by_sport = (
    ita_medals_unique
    .groupby("Sport")["Medal"]
    .count()
    .sort_values(ascending=False)
)

fig_medals_by_sport = px.bar(
    medals_by_sport.head(10),
    title="Top 10 sporter där Italien tagit flest medaljer",
    labels={"index": "Sport", "value": "Antal medaljer"},
)

# 2) Top 5 sports with most Italian participants
participants_by_sport = (
    ita
    .drop_duplicates(subset=["Games", "ID"])
    .groupby("Sport")["ID"]
    .count()
    .sort_values(ascending=False)
)

fig_participants_by_sport = px.bar(
    participants_by_sport.head(5),
    title="Top 5 sporter med flest italienska deltagare",
    labels={"index": "Sport", "value": "Antal deltagare"},
)

# 3) Summer vs Winter medals over time
# Summer
ita_summer_unique = (
    ita[
        (ita["Medal"] != "None") &
        (ita["Season"] == "Summer")
    ]
    .drop_duplicates(subset=["Games", "Event", "Medal"])
)

medals_by_games_summer = (
    ita_summer_unique
    .groupby("Games")["Medal"]
    .count()
    .reset_index()
)

fig_medals_summer = px.line(
    medals_by_games_summer,
    x="Games",
    y="Medal",
    title="Medaljer per OS - Italien Sommar",
    markers=True,
)

# Winter
ita_winter_unique = (
    ita[
        (ita["Medal"] != "None") &
        (ita["Season"] == "Winter")
    ]
    .drop_duplicates(subset=["Games", "Event", "Medal"])
)

medals_by_games_winter = (
    ita_winter_unique
    .groupby("Games")["Medal"]
    .count()
    .reset_index()
)

fig_medals_winter = px.line(
    medals_by_games_winter,
    x="Games",
    y="Medal",
    title="Medaljer per OS - Italien Vinter",
    markers=True,
)

# 4) Age distribution of Italian athletes
fig_age_hist = px.histogram(
    ita,
    x="Age",
    nbins=30,
    title="Åldersfördelning - Italienska OS-idrottare",
    labels={"Age": "Ålder"},
)

# 5) Sex distribution pie chart
fig_sex_pie = px.pie(
    ita,
    names="Sex",
    title="Könsfördelning - Italien",
)

# 6) Number of Italian participants per Games (Summer & Winter)
ita_summer_participants = (
    ita[ita["Season"] == "Summer"]
    .drop_duplicates(subset=["Games", "ID"])
    .groupby("Games")["ID"]
    .count()
    .reset_index()
)

fig_summer_participants = px.line(
    ita_summer_participants,
    x="Games",
    y="ID",
    title="Antal italienska deltagare per OS - Sommar",
    markers=True,
    labels={"ID": "Antal deltagare"},
)

ita_winter_participants = (
    ita[ita["Season"] == "Winter"]
    .drop_duplicates(subset=["Games", "ID"])
    .groupby("Games")["ID"]
    .count()
    .reset_index()
)

fig_winter_participants = px.line(
    ita_winter_participants,
    x="Games",
    y="ID",
    title="Antal italienska deltagare per OS - Vinter",
    markers=True,
    labels={"ID": "Antal deltagare"},
)

# ---- Figures: Fencing (Italy) ----

fencing = ita[ita["Sport"] == "Fencing"].copy()

fencing_unique_medals = (
    fencing[fencing["Medal"] != "None"]
    .drop_duplicates(subset=["Games", "Event", "Medal"])
)

# Medal types per year (Gold / Silver / Bronze stacked bar)
medals_by_type = (
    fencing_unique_medals
    .pivot_table(
        index="Year",
        columns="Medal",
        values="ID",
        aggfunc="count",
        fill_value=0,
    )
    .reset_index()
)

fig_fencing_medal_types = px.bar(
    medals_by_type,
    x="Year",
    y=["Gold", "Silver", "Bronze"],
    title="Italy Fencing - Medals per Year",
    labels={"value": "Number of Medals", "variable": "Medal Type"},
    color_discrete_map={
        "Gold": "#F6D411",
        "Silver": "#D7D4D4",
        "Bronze": "#CD7532",
    },
)
fig_fencing_medal_types.update_layout(barmode="stack")

# Total medals per year (line)
medals_type_cols = [
    c for c in medals_by_type.columns
    if c in ["Gold", "Silver", "Bronze"]
]
medals_by_type["Total"] = medals_by_type[medals_type_cols].sum(axis=1)

fig_fencing_total_medals = px.line(
    medals_by_type,
    x="Year",
    y="Total",
    markers=True,
    title="Italy Fencing - Total Medals per Year",
    labels={"Total": "Total Medals"},
)

# Medals by fencing event (Italy)
medals_by_event = (
    fencing_unique_medals
    .groupby("Event")["Medal"]
    .count()
    .sort_values(ascending=False)
    .reset_index()
)

fig_fencing_medals_by_event = px.bar(
    medals_by_event,
    x="Event",
    y="Medal",
    title="Italy Fencing - Medals per Event",
    labels={"Medal": "Number of Medals", "Event": "Event"},
)
fig_fencing_medals_by_event.update_xaxes(tickangle=45)

# ---- Figures: Fencing vs rest of the world / other sports ----

# Fencing for all countries
fencing_all = df[df["Sport"] == "Fencing"].copy()

fencing_all_unique_medals = (
    fencing_all[fencing_all["Medal"] != "None"]
    .drop_duplicates(subset=["Games", "Event", "Medal"])
)

medals_country = (
    fencing_all_unique_medals
    .groupby("NOC")["Medal"]
    .count()
    .reset_index()
    .sort_values("Medal", ascending=False)
)

fig_fencing_country_medals = px.bar(
    medals_country.head(20),
    x="NOC",
    y="Medal",
    title="Fencing - Medal Distribution by Country",
    labels={"NOC": "Country", "Medal": "Number of Medals"},
)

# Age distribution: Fencing vs other Italian sports
fencing_group = ita[ita["Sport"] == "Fencing"].copy()
fencing_group["Group"] = "Fencing"

other_sports = ita[ita["Sport"] != "Fencing"].copy()
other_sports["Group"] = "Other sports"

age_compare = pd.concat([fencing_group, other_sports], ignore_index=True)

mean_age = (
    age_compare.groupby("Group")["Age"]
    .mean()
    .reset_index()
    .round(1)
)

fig_age_fencing_vs_others = px.histogram(
    age_compare,
    x="Age",
    nbins=30,
    histnorm="percent",
    facet_row="Group",
    title="Age Distribution - Fencing vs Other Italian Sports",
    labels={"Age": "Age", "Group": "Group"},
)
fig_age_fencing_vs_others.update_layout(
    height=700,
    margin=dict(t=80, b=40),
    font=dict(size=14),
)
fig_age_fencing_vs_others.update_xaxes(range=[10, 50])
fig_age_fencing_vs_others.update_yaxes(matches=None)

# ---- Dash app layout ----

app = dash.Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "20px"},
    children=[
        html.H1("OS-analys: Italien & Fäktning", style={"textAlign": "center"}),

        html.H2("Italien – översikt"),
        dcc.Graph(figure=fig_medals_by_sport),
        dcc.Graph(figure=fig_participants_by_sport),
        dcc.Graph(figure=fig_medals_summer),
        dcc.Graph(figure=fig_medals_winter),
        dcc.Graph(figure=fig_age_hist),
        dcc.Graph(figure=fig_sex_pie),
        dcc.Graph(figure=fig_summer_participants),
        dcc.Graph(figure=fig_winter_participants),

        html.H2("Fencing – Italien"),
        dcc.Graph(figure=fig_fencing_medal_types),
        dcc.Graph(figure=fig_fencing_total_medals),
        dcc.Graph(figure=fig_fencing_medals_by_event),

        html.H2("Fencing – internationellt"),
        dcc.Graph(figure=fig_fencing_country_medals),

        html.H2("Åldersjämförelse: Fäktning vs övriga sporter"),
        dcc.Graph(figure=fig_age_fencing_vs_others),

        html.H3("Medelålder per grupp"),
        html.Ul(
            [
                html.Li(f"{row['Group']}: {row['Age']} år")
                for _, row in mean_age.iterrows()
            ]
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
