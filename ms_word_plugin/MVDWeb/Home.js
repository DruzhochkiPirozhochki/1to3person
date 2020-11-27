/*
(function () {
    "use strict";

    var messageBanner;

    // Функцию инициализации необходимо выполнять при каждой загрузке новой страницы.
    Office.initialize = function (reason) {
        $(document).ready(function () {
            // Инициализировать механизм уведомлений и скрыть его
            var element = document.querySelector('.MessageBanner');
            messageBanner = new components.MessageBanner(element);
            messageBanner.hideBanner();

            // Если не используется Word 2016, использовать резервную логику.
            if (!Office.context.requirements.isSetSupported('WordApi', '1.1')) {
                $("#template-description").text("В этом примере показан выделенный текст.");
                $('#button-text').text("Отобразить!");
                $('#button-desc').text("Отобразить выделенный текст");
                
                $('#highlight-button').click(displaySelectedText);
                return;
            }

            $("#template-description").text("В этом примере показано выделение самого длинного слова в тексте, выбранном в документе.");
            $('#button-text').text("Выделить!");
            $('#button-desc').text("Выделение самого длинного слова.");
            
            loadSampleData();

            // Добавить обработчик события щелчка кнопкой мыши для выделенной кнопки.
            $('#highlight-button').click(hightlightLongestWord);
        });
    };

    function loadSampleData() {
        // Запустить пакетную операцию для объектной модели Word.
        Word.run(function (context) {
            // Создать прокси-объект для основного текста документа.
            var body = context.document.body;

            // Поставить в очередь команду для очистки содержимого основного текста.
            body.clear();
            // Поставить в очередь команду для вставки текста в конец основного текста документа.
            body.insertText(
                "This is a sample text inserted in the document",
                Word.InsertLocation.end);

            // Синхронизировать состояние документа с помощью выполнения команд из очереди и возвратить обещание отобразить выполнение задания.
            return context.sync();
        })
        .catch(errorHandler);
    }

    function hightlightLongestWord() {
        Word.run(function (context) {
            // Поставить в очередь команду для получения текущего выделения и затем
            // создать прокси-объект диапазона с результатами.
            var range = context.document.getSelection();
            
            // Эта переменная хранит результаты поиска самого длинного слова.
            var searchResults;
            
            // Поставить в очередь команду для загрузки результата выделенного диапазона.
            context.load(range, 'text');

            // Синхронизировать состояние документа с помощью выполнения команд из очереди
            // и возвратить обещание отобразить выполнение задания.
            return context.sync()
                .then(function () {
                    // Получить самое длинное слово из выделения.
                    var words = range.text.split(/\s+/);
                    var longestWord = words.reduce(function (word1, word2) { return word1.length > word2.length ? word1 : word2; });

                    // Поставить в очередь команду поиска.
                    searchResults = range.search(longestWord, { matchCase: true, matchWholeWord: true });

                    // Поставить в очередь команду для загрузки свойства шрифта результатов.
                    context.load(searchResults, 'font');
                })
                .then(context.sync)
                .then(function () {
                    // Поставить в очередь команду для выделения результатов поиска.
                    searchResults.items[0].font.highlightColor = '#FFFF00'; // Желтый
                    searchResults.items[0].font.bold = true;
                })
                .then(context.sync);
        })
        .catch(errorHandler);
    } 


    function displaySelectedText() {
        Office.context.document.getSelectedDataAsync(Office.CoercionType.Text,
            function (result) {
                if (result.status === Office.AsyncResultStatus.Succeeded) {
                    showNotification('Выбранный текст:', '"' + result.value + '"');
                } else {
                    showNotification('Ошибка:', result.error.message);
                }
            });
    }

    //$$(Helper function for treating errors, $loc_script_taskpane_home_js_comment34$)$$
    function errorHandler(error) {
        // $$(Always be sure to catch any accumulated errors that bubble up from the Word.run execution., $loc_script_taskpane_home_js_comment35$)$$
        showNotification("Ошибка:", error);
        console.log("Error: " + error);
        if (error instanceof OfficeExtension.Error) {
            console.log("Debug info: " + JSON.stringify(error.debugInfo));
        }
    }

    // Вспомогательная функция для отображения уведомлений
    function showNotification(header, content) {
        $("#notification-header").text(header);
        $("#notification-body").text(content);
        messageBanner.showBanner();
        messageBanner.toggleExpansion();
    }
})();
*/
'use strict';

(function () {

    Office.onReady(function () {
        // Office is ready
        $(document).ready(function () {

            // The document is ready
            // Use this to check whether the API is supported in the Word client.
            if (Office.context.requirements.isSetSupported('WordApi', '1.1')) {
                // Do something that is only available via the new APIs
                $('#emerson').click(insertEmersonQuoteAtSelection);
                $('#checkhov').click(insertChekhovQuoteAtTheBeginning);
                $('#proverb').click(insertChineseProverbAtTheEnd);
                $('#supportedVersion').html('This code is using Word 2016 or later.');
            }
            else {
                // Just letting you know that this code will not work with your version of Word.
                $('#supportedVersion').html('This code requires Word 2016 or later.');
            }
        });
    });

    function insertEmersonQuoteAtSelection() {
        Word.run(function (context) {

            // Create a proxy object for the document.
            var thisDocument = context.document;

            // Queue a command to get the current selection.
            // Create a proxy range object for the selection.
            var range = thisDocument.getSelection;

            // Queue a command to replace the selected text.
            range.insertText('"Hitch your wagon to a star."\n', Word.InsertLocation.replace);   

            // Synchronize the document state by executing the queued commands,
            // and return a promise to indicate task completion.
            return context.sync().then(function () {
                console.log('Added a quote from Ralph Waldo Emerson.');
            });
        })
            .catch(function (error) {
                console.log('Error: ' + JSON.stringify(error));
                if (error instanceof OfficeExtension.Error) {
                    console.log('Debug info: ' + JSON.stringify(error.debugInfo));
                }
            });
    }

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

                // Get the message to be transformed and its index in the original text
                var res = parseMessage(text);
                var message = res[0];
                var messageIdx = res[1];

                Debug.writeln("DEBUG");
                Debug.writeln(text);
                Debug.writeln("\nFULLNAME");
                Debug.writeln(fullName);
                Debug.writeln("\nMESSAGE");
                Debug.writeln(message);
                Debug.writeln('\nMESSAGE INDEX');
                Debug.writeln(messageIdx);
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
        var token = 'Иные данные о личности';

        // Get index of the second char after the token
        var messageIdx = text.indexOf(token) + token.length + 1;

        // Get the string after the token
        var message = text.slice(messageIdx);

        return [message, messageIdx];
    }

    function insertChineseProverbAtTheEnd() {
        Word.run(function (context) {

            // Create a proxy object for the document body.
            var body = context.document.body;

            // Queue a command to insert text at the end of the document body.
            body.insertText('"To know the road ahead, ask those coming back."\n', Word.InsertLocation.end);

            // Synchronize the document state by executing the queued commands,
            // and return a promise to indicate task completion.
            return context.sync().then(function () {
                console.log('Added a quote from a Chinese proverb.');
            });
        })
            .catch(function (error) {
                console.log('Error: ' + JSON.stringify(error));
                if (error instanceof OfficeExtension.Error) {
                    console.log('Debug info: ' + JSON.stringify(error.debugInfo));
                }
            });
    }
})();