// let answerCount = 1;  // Keep track of the number of answers

// document.getElementById('add-answer-btn').addEventListener('click', function() {
//     var container = document.getElementById('answers-container');
//     var newAnswerInput = document.createElement('div');
//     newAnswerInput.classList.add('answer-item');
    
//     newAnswerInput.innerHTML = `
//         <input type="text" name="answer_text" placeholder="Treść odpowiedzi" class="form-control" required>
//         <input type="checkbox" name="is_correct" value="${answerCount}"> Odpowiedź poprawna

//     `;
//     print(answerCount)
//     container.appendChild(newAnswerInput);
    
//     newAnswerInput.querySelector('.remove-answer-btn').addEventListener('click', function() {
//         newAnswerInput.remove();
//     });
    
//     answerCount++;  // Increment the count after adding a new answer
// });
// {/* <button type="button" class="remove-answer-btn btn btn-danger position-absolute" style="top: 0; right: 0;">X</button> */}