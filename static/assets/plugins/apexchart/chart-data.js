'use strict';

$(document).ready(function () {

    // ===== Dynamic Learning Activity Chart =====
    if ($('#apexcharts-area').length > 0) {

        // Data injected from Django template
        // These are generated in student_dashboard view
        let labels = window.learningLabels || [];
        let scores = window.learningScores || [];

        // Fallback if no marks exist
        if (labels.length === 0) {
            labels = ['No Data'];
            scores = [0];
        }

        var options = {
            chart: {
                height: 350,
                type: "area",
                toolbar: { show: false },
            },
            dataLabels: { enabled: false },
            stroke: { curve: "smooth" },

            series: [
                {
                    name: "Your Scores",
                    color: "#FFBC53",
                    data: scores
                }
            ],

            xaxis: {
                categories: labels,
                title: {
                    text: "Tests / Subjects"
                }
            },

            yaxis: {
                min: 0,
                max: 100,
                title: {
                    text: "Marks (%)"
                }
            }
        };

        var chart = new ApexCharts(document.querySelector("#apexcharts-area"), options);
        chart.render();
    }

});
