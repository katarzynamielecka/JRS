const instructions = {
  "/systemadmin/": "Panel administratora. W sekcji 'Pracownicy' możliwe jest tworzenie oraz usuwanie kont pracowników. Sekcja 'Rekrutacja' umożliwia planowanie procesów rekrutacyjnych oraz wybór testów, które będą częścią tych rekrutacji. W sekcji 'Testy' administrator ma możliwość tworzenia testów, oceny ich wyników, przeglądania formularzy zapisu oraz przypisywania zarejestrowanych uczestników do odpowiednich kursów. Sekcja 'Obecność' pozwala na monitorowanie frekwencji oraz odwoływanie zajęć. W panelu 'Układanie planu lekcji' można zaplanować harmonogram zajęć. Przyciski 'Wyeksportuj dane pracowników', 'Wyeksportuj dane kursów' oraz 'Wyeksportuj zapisy na semestry' umożliwiają eksportowanie danych z systemu do bazy danych JRS.",
  "/systemadmin/employee-management": "Zarządzanie pracownikami w systemie administracyjnym.\nWyświetla listę kont pracowników z ich danymi. Użyj przycisku \"Usuń\", aby usunąć wybrane konto.",
  "/systemadmin/courses-management": "Zarządzanie kursami w systemie administracyjnym.\nAby zarejestrować kurs, najpierw dodaj semestr i język oraz upewnij się, że utworzono konta nauczycieli. Kurs, który odpowiada grupie zajęciowej, może być przeznaczony dla osób słowiańskojęzycznych lub niesłowiańskojęzycznych.\nKlikając \"Wybierz lektorów\", przypisz nauczycieli, którzy mogą prowadzić dany kurs. Użyj przycisku \"Kursanci\", aby wyświetlić listę przypisanych uczestników.",
  "/systemadmin/form-management": "Panel zarządzania testami językowymi. Umożliwia tworzenie i edytowanie testów. Po kliknięciu na wypełniony test można sprawdzić odpowiedzi i wystawić oceny. Panel zawiera również funkcje przypisywania uchodźców do kursów oraz przeglądania i odrzucania zgłoszeń na kursy.",
  "/systemadmin/recruitment_management": `Aby w pełni wykorzystać możliwości systemu i skutecznie zarządzać kursami językowymi, wykonaj następujące kroki:
1. Utwórz konta nauczycieli.
2. W panelu kursów dodaj semestr, języki nauczane oraz kursy językowe.
3. Przypisz nauczycieli do odpowiednich kursów.
4. W panelu testów stwórz testy językowe lub pozwól, aby zrobili to nauczyciele.
5. W panelu rekrutacji utwórz rekrutację i ustal jej zasady (maksymalna liczba osób, termin itp.).
6. Rekrutacja zakończy się automatycznie, gdy:
 - Liczba uczestników osiągnie maksymalny limit.
 - Minie termin zakończenia zapisów.
 Możesz także zakończyć ją ręcznie.
7. Po zakończeniu rekrutacji sprawdź testy językowe lub zleć to nauczycielom.
8. W panelu testów językowych przejrzyj zgłoszenia i w razie potrzeby usuń niektóre z nich.
9. Przypisz uczestników do grup na podstawie wyników testów.
10. W panelu układania planu lekcji zaplanuj harmonogram zajęć.
11. W panelu obecności nauczyciele mogą monitorować obecność uczestników.`,
  "/systemadmin/timetable/": "Panel do układania harmonogramu zajęć. Wprowadź przedziały czasowe (godziny lekcji) i dodaj sale. Upewnij się w panelu kursów, że każdy kurs ma przypisanego co najmniej jednego nauczyciela. Uzupełnij tabelę dostępności sal i lektorów. Po przygotowaniu danych naciśnij przycisk „Wygeneruj plan lekcji”. Jeśli wystąpią konflikty uniemożliwiające wygenerowanie planu, system poinformuje Cię o tym. Po wygenerowaniu planu możesz dostosować go ręcznie: przeciągaj lekcje, aby zmieniać ich położenie, lub kliknij dwukrotnie na lekcję, aby zmienić lektora lub salę.",
  "/systemadmin/refugees/<int:course_id>/": "Lista uchodźców przypisanych do wybranego kursu. Jeśli chcesz przenieść uczestnika do innego kursu, możesz to zrobić w panelu testów w sekcji „Przydzielanie kursantów do kursów językowych”.",
  "/systemadmin/assignment_to_courses/<int:test_id>/<str:recruitment_name>/": "Przypisanie do kursów na podstawie wyników testów.",
  "/systemadmin/edit_test/<int:id>/": "Edytowanie wybranego testu. Możesz dodawać pytania zamknięte i otwarte, a także ustalać maksymalną liczbę punktów za każde zadanie. Po wprowadzeniu punktacji pamiętaj o zapisaniu zmian.",
  "/systemadmin/create-test/": "Tworzenie nowego testu. Wprowadź nazwę testu, opis oraz wybierz język, z którego będzie przeprowadzony test. Pytania do testu można dodać w sekcji edytowania testu.",
  "/systemadmin/test-check/<int:test_id>/": "Panel do oceny testów językowych. Po kliknięciu 'Zobacz test' wyświetlone zostaną pytania oraz odpowiedzi. Pytania zamknięte oceniane są automatycznie, natomiast punktacja za odpowiedzi przyznawana jest w kolumnie 'Punkty'. Należy pamiętać o zapisaniu punktów po ich wprowadzeniu. W sekcji 'Przydzielanie kursantów do kursów' możliwe jest przypisanie uczestników do kursów na podstawie wyników testów lub ręcznie. W sekcji 'Formularze' można przeglądać dane zarejestrowanych osób oraz usuwać nieodpowiednie zgłoszenia.",
  "/systemadmin/register/": "Rejestracja kont pracowników i administratorów w systemie. Jeśli wybierzesz pole \"Czy administrator\", użytkownik będzie miał dostęp do danych kursantów oraz poszerzonych funkcjonalności systemu.\nW panelu pracownika użytkownik ma możliwość tworzenia testów językowych i oceny odpowiedzi oraz sprawdzania listy obecności na zajęciach i wydalenia kursanta z kursu.",
  "/systemadmin/attendance/": "Panel do zarządzania obecnościami. Można tu odwołać zajęcia lub anulować ich odwołanie. Aby sprawdzić obecność, kliknij wybrane zajęcia, a zostaniesz przekierowany do sekcji sprawdzania obecności.",
  "/systemadmin/mark-attendance/<int:schedule_id>/<str:date>/": "Oznaczanie obecności podczas wybranych zajęć. Status obecności można edytować w dowolnym momencie.",
  "/systemadmin/attendance/student/<int:refugee_id>/": "Przeglądanie obecności wybranego uchodźcy. Po naciśnięciu przyisku \"Usuń z kursu\" osoba zostanie usunięta z listy kursantów danego kursu.",
  "/systemadmin/send-email/": "Wysyłanie wiadomości e-mail.",
  "/systemadmin/send-email/to-course/<int:course_id>/": "Wysyłanie wiadomości e-mail do wszystkich uczestników wybranego kursu.",
  "/systemadmin/send-email/to-refugee/<int:refugee_id>/": "Wysyłanie wiadomości e-mail do wybranego kursanta/uchodźcy.",
  "/systemadmin/applications/<str:recruitment_name>/": "Lista zgłoszeń w rekrutacji - po naciśnięciu przycisku \"Usuń\" wybrane zgłoszenie zostanie usunięte z systemu.",
  "/employee/": "Panel lektora. W sekcji 'Obecność' można monitorować obecność na zajęciach oraz odwoływać zajęcia. W sekcji 'Testy' możliwe jest tworzenie, sprawdzanie oraz ocenianie testów językowych.",
  "/employee/form-management": "Panel testów w panelu pracownika umożliwia tworzenie nowych testów. W sekcji edytowania można dodawać pytania oraz definiować szczegóły testu. W sekcji 'Wypełnione testy' dostępna jest możliwość przeglądania wyników i oceny testów.",
  "/employee/test-check/<int:test_id>/": "Panel do sprawdzania testów językowych. Po naciśnięciu 'Zobacz test' wyświetlą się pytania oraz odpowiedzi. Pytania zamknięte są oceniane automatycznie. Punktacja za odpowiedzi przyznawana jest w kolumnie 'Punkty'. Należy pamiętać o zapisaniu punktów po ich wprowadzeniu.",
  "/employee/edit_test/<int:id>/": "Edytowanie wybranego testu. Możesz dodawać pytania zamknięte i otwarte, a także ustalać maksymalną liczbę punktów za każde zadanie. Po wprowadzeniu punktacji pamiętaj o zapisaniu zmian.",
  "/employee/create-test/": "Tworzenie nowego testu. Wprowadź nazwę testu, opis oraz wybierz język, z którego będzie przeprowadzony test. Pytania do testu można dodać w sekcji edytowania testu.",
  "/employee/attendance/": "Panel do zarządzania obecnościami. Można tu odwołać zajęcia lub anulować ich odwołanie. Aby sprawdzić obecność, kliknij wybrane zajęcia, a zostaniesz przekierowany do sekcji sprawdzania obecności.",
  "/employee/mark-attendance/<int:schedule_id>/<str:date>/": "Oznaczanie obecności podczas wybranych zajęć. Status obecności można edytować w dowolnym momencie.",
  "/employee/attendance/student/<int:refugee_id>/": "Przeglądanie obecności wybranego uchodźcy. Po naciśnięciu przyisku \"Usuń z kursu\" osoba zostanie usunięta z listy kursantów danego kursu.",
};

// Funkcja dopasowująca ścieżki z dynamicznymi zmiennymi
function matchPath(path) {
  for (const pattern in instructions) {
      const regex = new RegExp(
          "^" + pattern.replace(/<int:[^>]+>/g, "\\d+").replace(/<str:[^>]+>/g, "[^/]+") + "$"
      );
      if (regex.test(path)) {
          return instructions[pattern];
      }
  }
  return "Brak instrukcji dla tej podstrony.";
}

function setInstructions() {
  const path = window.location.pathname;
  const instructionText = matchPath(path);
  document.getElementById("instructionText").innerText = instructionText;
}

function toggleInstructions() {
  const popup = document.getElementById("instructionPopup");
  popup.style.display = popup.style.display === "block" ? "none" : "block";
}

window.onload = setInstructions;
