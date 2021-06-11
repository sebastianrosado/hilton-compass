import os  # type: ignore
from typing import Any, Optional

import dash  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
import dash_table  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
from dash.dependencies import Input, Output  # type: ignore

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# GA tag
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-159320752-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-159320752-1');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# Tab title
app.title = "Hilton Compass | Welcome"

# API keys and datasets
reviews = pd.read_csv(
    "https://raw.githubusercontent.com/sebastianrosado/hilton-compass/master/countries_trimmed.csv"
)

reviews = reviews[
    [
        "review_date",
        "hotel_name",
        "hotel_address",
        "average_score",
        "reviewer_nationality",
        "reviewer_score",
        "negative_review",
        "positive_review",
        "total_number_of_reviews_reviewer_has_given",
        "lat",
        "lng",
    ]
]

reviews.rename(
    columns={
        "hotel_name": "Hotel",
        "hotel_address": "Hotel Address",
        "average_score": "Average Rating",
        "review_date": "Review Date",
        "reviewer_nationality": "Reviewer Nationality",
        "reviewer_score": "Reviewer Score",
        "negative_review": "Negative Review",
        "positive_review": "Positive Review",
        "total_number_of_reviews_reviewer_has_given": "Total User Reviews Submitted",
        "lat": "Lat",
        "lng": "Lon",
    },
    inplace=True,
)

# String ratings with 43 rows for hovertext
reviews["Average Rating"] = reviews["Average Rating"].astype(str)
reduced_df = reviews.drop_duplicates(subset="Hotel", keep="last")
ratings = reduced_df["Average Rating"]

# Hotel names (43 rows) for hovertext
hotels = reviews["Hotel"].unique()

# Numeric ratings for marker color scales
df_copy = reviews.copy()
df_copy["Average Rating"] = pd.to_numeric(df_copy["Average Rating"])
reduced_df_copy = df_copy.drop_duplicates(subset="Hotel", keep="last")
df_copy["id"] = df_copy["Hotel"]
df_copy.set_index("id", inplace=True, drop=False)

# Value count dataset for marker size
value_counts = df_copy["Hotel"].value_counts()
value_counts_df = value_counts.rename_axis("Hotel").reset_index(name="Counts")

# Lower histogram table
histogram = value_counts_df
histogram = histogram.merge(
    reduced_df[["Hotel", "Average Rating"]],
    how="left",
    left_on="Hotel",
    right_on="Hotel",
)

# Dropdown dictionary
city_dict = {
    "city": ["Amsterdam", "Barcelona", "London", "Milan", "Paris", "Vienna"],
    "lat": [52.3545362, 41.3947688, 51.525826, 45.4017587, 48.8628612, 48.2205998],
    "lon": [4.7638774, 2.0787277, -0.2381047, 8.8486593, 2.1613319, 16.2399763],
}

city_df = pd.DataFrame(data=city_dict)

# MapBox API key
seabass_custom_style = os.environ["MAPBOX_STYLE"]

mapbox_access_token = os.environ["MAPBOX_KEY"]

# Map layout
fig2 = go.Figure(
    go.Scattermapbox(
        lat=list(reviews["Lat"].unique()),
        lon=list(reviews["Lon"].unique()),
        mode="markers",
        text=hotels,
        hovertext=ratings,
        marker=go.scattermapbox.Marker(
            size=list(value_counts_df["Counts"]),
            sizemin=4,
            sizeref=13,
            opacity=0.8,
            color=list(reduced_df_copy["Average Rating"]),
            cmin=7.0,
            cmax=9.5,
            reversescale=True,
        ),
        hovertemplate="<b>%{text}</b><br>"
        + "Average Rating: %{hovertext}<br>"
        + "Total Reviews: %{marker.size:,}"
        "<extra></extra>",
    )
)

fig2.update_layout(
    hovermode="closest",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        style="light",
        bearing=0,
        center=go.layout.mapbox.Center(lat=48.7329446, lon=5.0126286),
        pitch=0,
        zoom=2.5,
    ),
)

# Tab styles
tabs_styles = {"height": "44px", "font-size": "1.2vw"}

tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding-top": "8px",
    "padding-left": "6px",
    "padding-right": "6px",
    "padding-bottom": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#119DFF",
    "color": "white",
    "padding-top": "8px",
    "padding-left": "6px",
    "padding-right": "6px",
    "padding-bottom": "6px",
}

# Other styling

colors = {"banner": "#18496E", "text": "#FFFFFF"}

# App layout

app.layout = html.Div(
    [
        #     Titles
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            children="Hilton Compass",
                            style={
                                "color": colors["text"],
                                "font-family": "Helvetica Neue !important",
                                "letter-spacing": "1px",
                                "font-weight": "200 !important",
                                "margin-top": "3%",
                                "margin-left": "5%",
                                "margin-bottom": 0,
                            },
                        ),
                        html.H5(
                            children="A hotel visualization, based on reviews",
                            style={
                                "color": colors["text"],
                                "margin-bottom": "3%",
                                "margin-left": "5%",
                                "font-family": "Helvetica Neue !important",
                                "letter-spacing": "1px",
                                "font-weight": "200 !important",
                            },
                        ),
                    ],
                    className="eight columns",
                ),
                html.Div(
                    [
                        html.A(
                            id="gh-link",
                            children="View on GitHub",
                            href="https://github.com/sebastianrosado/hilton-compass",
                            target="_blank",
                            style={
                                "color": "white",
                                "text-align": "center",
                                "border": "solid 1px white",
                                "text-decoration": "none",
                                "font-family": "HelveticaNeue",
                                "border-radius": "2px",
                                "padding": "2px",
                                "padding-top": "5px",
                                "padding-left": "15px",
                                "padding-right": "15px",
                                "font-weight": "100",
                                "position": "absolute",
                                "margin-bottom": 0,
                                "margin-top": "3.5%",
                                "margin-right": 0,
                                "margin-left": "6.5%",
                                "transition-duration": "400ms",
                            },
                        ),
                        html.Img(
                            src="assets/GitHub-Mark-Light-64px.png",
                            style={
                                "height": "36px",
                                "margin-top": "14%",
                                "margin-left": "9%",
                                "padding-left": "2%",
                                "padding-top": "2%",
                            },
                        ),
                    ],
                    style={"padding-left": "5%"},
                    className="four columns",
                ),
            ],
            style={
                "margin-bottom": 0,
                "background-color": colors["banner"],
                "border-radius": "4px",
                "margin-top": 12,
                "box-shadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
                "transition": "all 0.3s cubic-bezier(.25,.8,.25,1)",
            },
            className="row",
        ),
        # Description & About Tabs
        html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="Home",
                            children=[
                                html.P(
                                    id="home",
                                    children=[
                                        "In an age where the consumer increasingly relies on algorithms in order to make decisions "
                                        "about where to eat, what to watch and where to sleep, hotel reviews matter. In fact, "
                                        "your hotel's reputation can be the difference between being profitable and losing money. "
                                        "Studies ",
                                        html.A(
                                            "suggest ",
                                            href="https://scholarship.sha.cornell.edu/chrpubs/5/",
                                            target="_blank",
                                        ),
                                        "that if a hotel's review score increases by 1 point on a 5-point scale, ",
                                        html.B(
                                            "the hotel would be able to increase its room prices by 11.2 percent and still maintain "
                                            "the same occupancy or market share."
                                        ),
                                    ],
                                    style={"font-size": "1.2vw", "margin-top": 3},
                                ),
                                dcc.Markdown(
                                    id="home-2",
                                    children="The first step to increasing profit margins is to understand where you are "
                                    "underperforming. The second step is to understand why. We can do this with "
                                    "numerical and written reviews, respectively. On this page, you can explore two "
                                    "years of compiled reviews that guests from Australia, Canada, New Zealand and "
                                    "the United States wrote for various Hilton Hotels across Europe. If you want "
                                    "to read more on why these particular nationalities have been selected, "
                                    "start on the About tab. Thank you for visiting.",
                                    style={"font-size": "1.2vw"},
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style,
                        ),
                        dcc.Tab(
                            label="About",
                            children=[
                                html.P(
                                    id="about",
                                    children=[
                                        "This project began with a question: ",
                                        html.B(
                                            "Do people from different nationalities rate the same hotels differently? "
                                        ),
                                        "I found a dataset scraped from public reviews on Booking.com and posted on ",
                                        html.A(
                                            "Kaggle",
                                            href="https://www.kaggle.com/jiashenliu/515k-hotel-reviews-data-in-europe",
                                            target="_blank",
                                        ),
                                        " that helped me begin to answer that question. That dataset contains 515,738 entries "
                                        "and 17 columns of reviews of different hotels ",
                                        html.B("within Europe"),
                                        " spanning from 2015 to 2017. I chose to focus on Hilton Hotels because they had 35,"
                                        "490 review entries - the highest of any hotel group in the sample. Of those, 1,"
                                        "202 are reviews by Americans, 967 are by Australians, 336 are by Canadians and 196 are "
                                        "by New Zealanders. I focused on English-speaking countries because of the location of "
                                        "these countries relative to Europe and because I believe a common language makes any "
                                        "insights gained from this study more translatable across markets. ",
                                    ],
                                    style={"font-size": "1.2vw", "margin-top": 3},
                                ),
                                html.P(
                                    id="about-2",
                                    children=[
                                        "I ran an A/B experiment on the data with the null hypothesis that there is no significant "
                                        "difference between the average review score in North America (United States and Canada) "
                                        "versus that of English-speaking Oceania (Australia and New Zealand). If you want to see the "
                                        "complete study and its results, you can find it ",
                                        html.A(
                                            "here",
                                            href="https://github.com/sebastianrosado/hilton-experimental-design/blob/master/Hilton"
                                            "%20Experimental%20Design%20Project.ipynb",
                                            target="_blank",
                                        ),
                                        ".",
                                        html.B(
                                            " Teaser: there is in fact a statistically significant difference between the review "
                                            "scores of two different nationalities."
                                        ),
                                    ],
                                    style={"font-size": "1.2vw"},
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style,
                        ),
                    ],
                    style=tabs_styles,
                ),
            ],
            style={
                "margin-top": "1",
                "max-width": "100%",
            },
        ),
        # Dropdown Menu
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Where do you want to go next?"),
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {"label": "Anywhere", "value": "Anywhere"},
                                        {"label": "Amsterdam", "value": "Amsterdam"},
                                        {"label": "Barcelona", "value": "Barcelona"},
                                        {"label": "London", "value": "London"},
                                        {"label": "Milan", "value": "Milan"},
                                        {"label": "Paris", "value": "Paris"},
                                        {"label": "Vienna", "value": "Vienna"},
                                    ],
                                    value="Anywhere",
                                ),
                            ],
                            style={
                                "margin-top": "1%",
                                "margin-bottom": "2%",
                                "text-align": "center",
                                "fontWeight": "800",
                                "fontFamily": "HelveticaNeue",
                            },
                        )
                    ]
                )
            ],
            className="row",
        ),
        # Map
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="map-graph",
                            figure=fig2,
                            style={"height": "60vh", "width": "100%"},
                            config={"displayModeBar": False},
                        )
                    ],
                    className="six columns",
                ),
                # Table
                html.Div(
                    [
                        dash_table.DataTable(
                            id="datatable",
                            columns=[
                                {"name": i, "id": i}
                                for i in df_copy.columns
                                if i != "id"
                            ],
                            data=df_copy.to_dict("records"),
                            fixed_rows={"headers": False, "data": 0},
                            row_selectable="single",
                            derived_virtual_selected_rows=None,
                            sort_action="native",
                            sort_mode="multi",
                            style_cell_conditional=[
                                {"if": {"column_id": c}, "textAlign": "left"}
                                for c in [
                                    "Hotel",
                                    "Hotel Address",
                                    "Reviewer Nationality",
                                    "Negative Review",
                                    "Positive Review",
                                ]
                            ],
                            style_table={
                                "overflowY": "auto",
                                "maxHeight": "60vh",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                }
                            ],
                            style_header={
                                "backgroundColor": "#C1CCD7",
                                "fontWeight": "bold",
                                "font_size": "1vw",
                            },
                            style_data={"font-size": "0.8vw"},
                            style_cell={
                                "minWidth": "140px",
                                "width": "140px",
                                "maxWidth": "300px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "font-family": "HelveticaNeue",
                            },
                        ),
                        html.Div(id="datatable-container"),
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        # Positive Review
        html.Div(
            [
                html.H5(
                    id="positive-textbox-header",
                    children="Positive Review",
                    style={"text-align": "center"},
                ),
                dcc.Textarea(
                    id="positive-textbox",
                    placeholder="Select a row to see the positive written review...",
                    contentEditable=False,
                    readOnly=True,
                    style={
                        "width": "100%",
                        "fontFamily": "HelveticaNeue",
                        "fontWeight": "normal",
                    },
                ),
            ]
        ),
        # Negative Review
        html.Div(
            [
                html.H5(
                    id="negative-textbox-header",
                    children="Negative Review",
                    style={"text-align": "center"},
                ),
                dcc.Textarea(
                    id="negative-textbox",
                    placeholder="Select a row to see the negative written review...",
                    contentEditable=False,
                    readOnly=True,
                    style={"width": "100%", "fontFamily": "HelveticaNeue"},
                ),
            ]
        ),
        # Bar plot
        html.Div(
            [
                dcc.Graph(
                    id="Hotel",
                    figure={
                        "data": [
                            {
                                "x": histogram["Hotel"],
                                "y": histogram["Average Rating"],
                                "type": "bar",
                                "marker": {
                                    "color": list(reduced_df_copy["Average Rating"]),
                                    "cmin": 7.0,
                                    "cmax": 9.5,
                                    "reversescale": True,
                                },
                            }
                        ],
                        "layout": {
                            "xaxis": {
                                "visible": False,
                                "automargin": True,
                                "tickangle": -90,
                            },
                            "paper_bgcolor": "#F4F4F2",
                            "plot_bgcolor": "#F4F4F2",
                            "yaxis": {
                                "automargin": True,
                                "title": {"text": "Average Ratings"},
                            },
                            "height": 250,
                            "margin": {"t": 5, "l": 10, "r": 10},
                        },
                    },
                )
            ],
            style={"margin-bottom": 0},
        ),
        html.Div(
            style={"marginLeft": "1.5%", "marginRight": "1.5%"},
            children=[
                html.P(
                    style={"textAlign": "center", "margin": "auto"},
                    children=[
                        "Full project on ",
                        html.A(
                            "GitHub",
                            href="https://github.com/sebastianrosado/hilton-experimental-design/blob"
                            "/master/Hilton%20Experimental%20Design%20Project.ipynb",
                            target="_blank",
                        ),
                        " | Developed by ",
                        html.A(
                            "Sebastian Rosado",
                            href="https://www.linkedin.com/in/srosadomustafa/",
                            target="_blank",
                        ),
                        " | Thanks for visiting 👋",
                    ],
                )
            ],
        ),
    ],
    className="ten columns offset-by-one",
)


# Callbacks
@app.callback(Output("map-graph", "figure"), [Input("location-dropdown", "value")])
def update_map_location(value: str):
    """Move map view to area of selected city.

    Parameters
    ----------
    value
        The city selected from the dropdown menu. If no city is selected ('Anywhere'),
        the map will move to a default position.

    Returns
    -------
    Object
        Returns map figure with updated parameters.

    """
    dff = city_df

    fig2.update_layout(
        hovermode="closest",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            style="light",
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=48.7329446
                if value == "Anywhere"
                else dff.loc[dff["city"] == value, "lat"].values[0],
                lon=5.0126286
                if value == "Anywhere"
                else dff.loc[dff["city"] == value, "lon"].values[0],
            ),
            pitch=0,
            zoom=2.5 if value == "Anywhere" else 8,
        ),
    )

    return fig2


@app.callback(
    Output("positive-textbox", "value"),
    [Input("datatable", "derived_virtual_selected_rows")],
)
def update_positive_reviews(derived_virtual_selected_rows: int) -> Optional[Any]:
    """Display selected positive hotel review in the positive review box.

    Parameters
    ----------
    derived_virtual_selected_rows
        Index value for the row you want to display in the review box.
        This parameter is NoneType with no rows selected.

    Returns
    -------
    None, String

    """
    dff = reviews
    return (
        None
        if not derived_virtual_selected_rows
        else dff["Positive Review"][derived_virtual_selected_rows]
    )


@app.callback(
    Output("negative-textbox", "value"),
    [Input("datatable", "derived_virtual_selected_rows")],
)
def update_negative_reviews(derived_virtual_selected_rows: int) -> Optional[Any]:
    """Display selected negative hotel review in the negative review box.

    Parameters
    ----------
    derived_virtual_selected_rows
        Index value for the row you want to display in the review box.
        This parameter is NoneType with no rows selected.

    Returns
    -------
    None, String

    """
    dff = reviews
    return (
        None
        if not derived_virtual_selected_rows
        else dff["Negative Review"][derived_virtual_selected_rows]
    )


if __name__ == "__main__":
    app.run_server(debug=False)
