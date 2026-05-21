import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove auto-scan listener
html = re.sub(r'textarea\.addEventListener\("input", async \(\) => \{.*?\n\}\);\n', '', html, flags=re.DOTALL)

# 2. Remove SMTP config HTML
html = re.sub(r'<div class="smtp-config">.*?</div>\n\s*</div>\n\s*<button class="btn-analyze" id="sendBtn"', '<button class="btn-analyze" id="sendBtn"', html, flags=re.DOTALL)

# 3. Create two result panels
analyze_panel = """
        <!-- Analyze Result -->
        <div class="result" id="analyzeResultPanel">
            <div class="result__header">
                <div class="result__icon" id="analyzeResultIcon"></div>
                <div>
                    <div class="result__tag" id="analyzeResultTag"></div>
                    <div class="result__title" id="analyzeResultTitle"></div>
                </div>
            </div>
            <div class="confidence-bar" id="analyzeConfidenceBar" style="display:none;">
                <div class="confidence-bar__header">
                    <span>Confidence</span>
                    <span id="analyzeConfidenceValue">0%</span>
                </div>
                <div class="confidence-bar__track">
                    <div class="confidence-bar__fill" id="analyzeConfidenceFill"></div>
                </div>
            </div>
        </div>
"""

compose_panel = """
        <!-- Compose Result -->
        <div class="result" id="composeResultPanel">
            <div class="result__header">
                <div class="result__icon" id="composeResultIcon"></div>
                <div>
                    <div class="result__tag" id="composeResultTag"></div>
                    <div class="result__title" id="composeResultTitle"></div>
                </div>
            </div>
            <div class="confidence-bar" id="composeConfidenceBar" style="display:none;">
                <div class="confidence-bar__header">
                    <span>Confidence</span>
                    <span id="composeConfidenceValue">0%</span>
                </div>
                <div class="confidence-bar__track">
                    <div class="confidence-bar__fill" id="composeConfidenceFill"></div>
                </div>
            </div>
        </div>
"""

# Insert analyze_panel inside contentAnalyze
html = re.sub(r'(<button class="btn-analyze" id="analyzeBtn".*?</button>\n\s*)</div>', r'\1' + analyze_panel + '        </div>', html, flags=re.DOTALL)

# Insert compose_panel inside contentCompose
html = re.sub(r'(<button class="btn-analyze" id="sendBtn".*?</button>\n\s*)</div>', r'\1' + compose_panel + '        </div>', html, flags=re.DOTALL)

# Remove the old shared resultPanel
html = re.sub(r'<!-- Result -->\s*<div class="result" id="resultPanel">.*?</div>\s*</div>\s*</main>', '</main>', html, flags=re.DOTALL)

# Update JS hideResult
html = html.replace("document.getElementById('resultPanel')", "document.getElementById('analyzeResultPanel').classList.remove('visible');\n        document.getElementById('composeResultPanel')")

# Update JS showResult
new_show_result = """
    function showResult(tab, type, icon, tag, title, confidence) {
        const panel = document.getElementById(tab + 'ResultPanel');
        const resultIcon = document.getElementById(tab + 'ResultIcon');
        const resultTag = document.getElementById(tab + 'ResultTag');
        const resultTitle = document.getElementById(tab + 'ResultTitle');
        const confBar = document.getElementById(tab + 'ConfidenceBar');
        const confValue = document.getElementById(tab + 'ConfidenceValue');
        const confFill = document.getElementById(tab + 'ConfidenceFill');

        // Reset
        panel.className = 'result visible result--' + type;
        resultIcon.textContent = icon;
        resultTag.textContent = tag;
        resultTitle.textContent = title;

        if (confidence !== undefined && (type === 'spam' || type === 'safe' || type === 'error')) {
            confBar.style.display = 'block';
            confValue.textContent = 'Spam Probability: ' + confidence + '%';
            // Animate the fill bar
            confFill.style.width = '0';
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    confFill.style.width = confidence + '%';
                });
            });
        } else {
            confBar.style.display = 'none';
        }
    }
"""
html = re.sub(r'function showResult\(type, icon, tag, title, confidence\).*?\}\n    \}', new_show_result.strip(), html, flags=re.DOTALL)

# Update analyzeEmail calls to showResult
html = html.replace("showResult('error'", "showResult('analyze', 'error'")
html = html.replace("showResult('loading'", "showResult('analyze', 'loading'")
html = html.replace("showResult('spam'", "showResult('analyze', 'spam'")
html = html.replace("showResult('safe'", "showResult('analyze', 'safe'")

# Update sendEmail function
html = re.sub(r'const smtpServer = .*?;\n\s*const smtpPort = .*?;\n\s*const fromEmail = .*?;\n\s*const fromPassword = .*?;', '', html)
html = html.replace("!toEmail || !subject || !body || !smtpServer || !fromEmail || !fromPassword", "!toEmail || !subject || !body")
html = html.replace("smtp_server: smtpServer,\n                    smtp_port: parseInt(smtpPort),\n                    from_email: fromEmail,\n                    from_password: fromPassword", "")

html = html.replace("showResult('analyze', 'error', '⚠️', 'Error', 'Please fill in all fields', 0);", "showResult('compose', 'error', '⚠️', 'Error', 'Please fill in all fields', 0);")
html = html.replace("showResult('analyze', 'spam', '🚨', 'Email Sent', `Spam Email Detected`, spamConfidence);", "showResult('compose', 'spam', '🚨', 'Email Sent', `Spam Email Detected`, spamConfidence);")
html = html.replace("showResult('analyze', 'safe', '✅', 'Email Sent', `Safe Email`, spamConfidence);", "showResult('compose', 'safe', '✅', 'Email Sent', `Safe Email`, spamConfidence);")
html = html.replace("showResult('analyze', 'error', '❌', 'Error', data.error || 'Failed to send email', 0);", "showResult('compose', 'error', '❌', 'Error', data.error || 'Failed to send email', 0);")
html = html.replace("showResult('analyze', 'error', '🔌', 'Error', 'Network error. Is the server running?', 0);", "showResult('compose', 'error', '🔌', 'Error', 'Network error. Is the server running?', 0);")


with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
