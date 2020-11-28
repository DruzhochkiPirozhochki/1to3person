'use strict';

(function () {

    Office.onReady(function () {
        // Office is ready
        $(document).ready(function () {
            // The document is ready
            // Use this to check whether the API is supported in the Word client.
            if (Office.context.requirements.isSetSupported('WordApi', '1.1')) {
                // Do something that is only available via the new APIs
                $('#transform').click(insertChekhovQuoteAtTheBeginning);
                $('#supportedVersion').html('This code is using Word 2016 or later.');
            }
            else {
                // Just letting you know that this code will not work with your version of Word.
                $('#supportedVersion').html('This code requires Word 2016 or later.');
            }
        });
    });


    function insertChekhovQuoteAtTheBeginning() {

        Word.run(function (context) {
            // Create a proxy object for the document body.
            var body = context.document.body

            // Load the text from the document
            context.load(body)

            // Synchronize the document state by executing the queued commands,
            // and return a promise to indicate task completion.
            return context.sync().then(function () {
                // Get the full text of the document (note that it is a single line - no \n characters
                var text = body.text;

                // Get the full name of the actor
                var fullName = parseFullName(text);

                // Get highlighted text
                getHighlightedText(fullName, text);                
            });
        })
            .catch(function (error) {
                console.log('Error: ' + JSON.stringify(error));
                if (error instanceof OfficeExtension.Error) {
                    console.log('Debug info: ' + JSON.stringify(error.debugInfo));
                }
            });
    }


    function parseFullName(text) {
        // Remove all digits
        var digitlessRow = text.replace(/[0-9]/g, '');

        // Get the list of words
        var words = digitlessRow.match(/[\wа-я]+/ig);
        var wordsLowerCase = words.map(x => x.toLowerCase());

        // Get indices of middle name and date of birth in the word list. Full name is in between those words
        var middleNameIdx = wordsLowerCase.indexOf('отчество');
        var dateOfBirthIdx = wordsLowerCase.slice(middleNameIdx + 1).indexOf('дата') + (middleNameIdx + 1);

        // Get the full name
        var fullName = words.slice(middleNameIdx + 1, dateOfBirthIdx);

        // Join all
        fullName = fullName.join(' ');

        return fullName;
    }


    function parseMessage(text) {
        // Consider message to be everything after this phrase
        const token = 'Иные данные о личности';

        // Get index of the second char after the token
        var messageIdx = text.indexOf(token) + token.length + 1;

        // Get the string after the token
        var message = text.slice(messageIdx);

        return [message, messageIdx];
    }

    function parseHighlightedMessage(text, highlightedText) {
        if (highlightedText !== null && highlightedText !== undefined) {
            // Get the start and end position of the highlighted text
            var startIdx = text.indexOf(highlightedText);
            var endIdx = startIdx + highlightedText.length;

            return [highlightedText, startIdx, endIdx];   
        } else {
            return ['', -1, -1];
        }
    }


    // Get highlighted text
    function getHighlightedText(fullName, text) {
        Office.onReady(function () {
            $(document).ready(function () {
                Office.context.document.getSelectedDataAsync(Office.CoercionType.Text, function (asyncResult) {
                    if (asyncResult.status == Office.AsyncResultStatus.Failed) {
                        Debug.writeln('Action failed. Error: ' + asyncResult.error.message);
                    }
                    else {
                        Debug.writeln('HIGHLIGHTED');
                        Debug.writeln(asyncResult.value);
                        var highlightedText = asyncResult.value;

                        var tmp = parseHighlightedMessage(text, highlightedText);
                        var message = tmp[0];
                        var messageStartIdx = tmp[1];
                        var messageEndIdx = tmp[2];

                        Debug.writeln("\nDEBUG");
                        Debug.writeln(text);
                        Debug.writeln("\nFULLNAME");
                        Debug.writeln(fullName);
                        Debug.writeln("\nMESSAGE");
                        Debug.writeln(message);
                        Debug.writeln('\nMESSAGE INDEX');
                        Debug.writeln(messageStartIdx + ':::' + messageEndIdx);

                        // Transform message and replace it with the result from server
                        transformText(fullName, message).then(res => {
                            Debug.writeln("\nTRANSFORMED TEXT");
                            Debug.writeln(res);

                            replaceText(res);
                        });
                    }
                });
            });
        });
    }

    /* Send POST request to the server to obtain the transformed version of the text */
    async function transformText(fullName, message) {
        // Parameters of the POST request
        const params = {
            'fname': fullName,
            'text': message
        };

        // Address of the server
        const url = 'http://localhost:8080/send';

        // Send POST request
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            // Get the transformed text
            var result = await response.json();

            Debug.writeln('\nRESPONSE');
            Debug.writeln(response);
            Debug.writeln('\nRESULT');
            Debug.writeln(result);

            return result['text'];

        } catch (e) {
            Debug.writeln('\nERROR');
            Debug.writeln(e);
        }
    }

    // Set a highlighted text to the string
    function replaceText(transformedText) {
        Office.onReady(function () {
            $(document).ready(function () {
                Office.context.document.setSelectedDataAsync(transformedText, function (asyncResult) {
                    if (asyncResult.status == Office.AsyncResultStatus.Failed) {
                        Debug.writeln('Action failed. Error: ' + asyncResult.error.message);
                    }
                });
            });
        });
    }

})();