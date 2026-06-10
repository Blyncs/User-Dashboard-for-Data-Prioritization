import pandas as pd

# 1. Your dataframe processing logic goes here
data = {
    "Project": ["Project A", "Project B", "Project C"],
    "Priority_Score": [85, 40, 95]
}
df = pd.DataFrame(data)

# Extract your columns for the JavaScript chart
labels = df["Project"].tolist()
scores = df["Priority_Score"].tolist()

# 2. Build the website raw HTML code using a python f-string
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 40px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h2 {{ text-align: center; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Project Priority Scores</h2>
        <canvas id="priorityChart" width="400" height="200"></canvas>
    </div>

    <script>
        const labels = {labels};
        const scores = {scores};

        // Replicate your YlOrRd style logic directly in the browser
        const backgroundColors = scores.map(score => {{
            if (score > 80) return 'rgba(217, 83, 79, 0.8)';  // High Priority (Red-ish)
            if (score > 50) return 'rgba(240, 173, 78, 0.8)'; // Medium Priority (Orange)
            return 'rgba(92, 184, 92, 0.8)';                 // Low Priority (Green)
        }});

        const ctx = document.getElementById('priorityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Priority Score',
                    data: scores,
                    backgroundColor: backgroundColors,
                    borderWidth: 1
                }}]
            }},
            options: {{ scales: {{ y: {{ beginAtZero: true, max: 100 }} }} }}
        }});
    </script>
</body>
</html>"""

# 3. Save the generated website file
with open("index.html", "w") as f:
    f.write(html_content)

print("Dashboard built successfully!")