(function () {
  "use strict";
  var QUIZZES = {};

  function register(id, questions) {
    QUIZZES[id] = questions;
  }

  function buildQuiz(container, questions) {
    var id = container.dataset.quizId;
    container.innerHTML =
      '<h2>\uD83E\uDDE0 Knowledge Check</h2>' +
      '<p class="kc-subtitle">Test your understanding before moving on. Select an answer for each question, then click <strong>Check Answers</strong>.</p>' +
      '<div class="kc-questions"></div>' +
      '<div class="kc-actions">' +
        '<button class="kc-submit-btn" data-action="submit">Check Answers</button>' +
        '<button class="kc-reset-btn" data-action="reset" style="display:none">Try Again</button>' +
      '</div>' +
      '<div class="kc-score-banner"></div>';

    var qWrap = container.querySelector(".kc-questions");

    questions.forEach(function (q, qi) {
      var block = document.createElement("div");
      block.className = "kc-question-block";
      block.dataset.qi = qi;
      var opts = q.options.map(function (opt, oi) {
        return '<label><input type="radio" name="kc-' + id + '-q' + qi + '" value="' + oi + '" />' + opt + '</label>';
      }).join("");
      block.innerHTML =
        '<div class="kc-question-text">Q' + (qi + 1) + '. ' + q.question + '</div>' +
        '<div class="kc-options">' + opts + '</div>' +
        '<div class="kc-feedback"></div>' +
        '<div class="kc-explanation"></div>';
      qWrap.appendChild(block);
    });

    container.querySelector('[data-action="submit"]').addEventListener("click", function () {
      var score = 0;
      var answered = 0;
      questions.forEach(function (q, qi) {
        var block = qWrap.children[qi];
        var selected = block.querySelector('input[name="kc-' + id + '-q' + qi + '"]:checked');
        var feedback = block.querySelector(".kc-feedback");
        var explanation = block.querySelector(".kc-explanation");
        if (!selected) return;
        answered++;
        var val = parseInt(selected.value, 10);
        var isCorrect = val === q.correct;
        if (isCorrect) {
          score++;
          block.classList.add("correct");
          block.classList.remove("wrong");
          feedback.textContent = "\u2705 Correct!";
          feedback.className = "kc-feedback visible correct";
        } else {
          block.classList.add("wrong");
          block.classList.remove("correct");
          feedback.textContent = "\u274C Incorrect. The correct answer is: \"" + q.options[q.correct] + "\"";
          feedback.className = "kc-feedback visible wrong";
        }
        explanation.textContent = q.explanation;
        explanation.className = "kc-explanation visible";
        block.querySelectorAll("input").forEach(function (r) { r.disabled = true; });
      });
      if (answered < questions.length) {
        alert("Please answer all questions before checking.");
        return;
      }
      var banner = container.querySelector(".kc-score-banner");
      var pct = Math.round((score / questions.length) * 100);
      if (pct === 100) {
        banner.textContent = "\uD83C\uDF89 Perfect score! " + score + "/" + questions.length + " \u2014 Great work!";
        banner.className = "kc-score-banner visible perfect";
      } else if (pct >= 60) {
        banner.textContent = "\uD83D\uDC4D Good effort! " + score + "/" + questions.length + " (" + pct + "%) \u2014 Review the explanations and keep going.";
        banner.className = "kc-score-banner visible good";
      } else {
        banner.textContent = "\uD83D\uDCDA " + score + "/" + questions.length + " (" + pct + "%) \u2014 Review the section and try again.";
        banner.className = "kc-score-banner visible retry";
      }
      container.querySelector('[data-action="submit"]').disabled = true;
      container.querySelector('[data-action="reset"]').style.display = "inline-block";
    });

    container.querySelector('[data-action="reset"]').addEventListener("click", function () {
      buildQuiz(container, questions);
    });
  }

  function init() {
    document.querySelectorAll(".knowledge-check[data-quiz-id]").forEach(function (container) {
      var id = container.dataset.quizId;
      if (QUIZZES[id]) buildQuiz(container, QUIZZES[id]);
    });
  }

  window.MLOpsQuiz = { register: register, init: init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
