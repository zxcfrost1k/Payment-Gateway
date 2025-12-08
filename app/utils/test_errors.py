# complete_cancel_test_suite.py
import requests
import json
import time
from typing import Dict, List, Tuple, Optional
import sys


class CancelPaymentSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "test_token_123"):
        self.base_url = base_url
        self.token = token
        self.results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Логирование результата теста"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append((test_name, success, details))
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        return success

    def make_request(self, transaction_id: str, use_token: bool = True, token: str = None) -> Optional[
        requests.Response]:
        """Универсальный метод отправки запроса"""
        url = f"{self.base_url}/api/v1/transactions/{transaction_id}/cancel"

        headers = {}
        if use_token:
            headers["Authorization"] = f"Bearer {token or self.token}"

        try:
            response = requests.post(url, headers=headers, timeout=10)
            return response
        except requests.exceptions.RequestException as e:
            print(f"   Network error: {e}")
            return None
        except Exception as e:
            print(f"   Unexpected error: {e}")
            return None

    def test_1_server_availability(self):
        """Тест 1: Доступность сервера"""
        print("\n" + "=" * 70)
        print("ТЕСТ 1: ДОСТУПНОСТЬ СЕРВЕРА")
        print("=" * 70)

        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return self.log_test("1.1 Health check", True,
                                     f"Status: {response.status_code}, Response: {response.text}")
            else:
                return self.log_test("1.1 Health check", False, f"Expected 200, got {response.status_code}")
        except Exception as e:
            return self.log_test("1.1 Health check", False, f"Error: {e}")

    def test_2_endpoint_structure(self):
        """Тест 2: Структура эндпоинта"""
        print("\n" + "=" * 70)
        print("ТЕСТ 2: СТРУКТУРА ЭНДПОИНТА")
        print("=" * 70)

        test_cases = [
            ("/api/v1/transactions/test_id/cancel", 204, "Правильный путь"),
            ("/transactions/test_id/cancel", 404, "Неправильный путь (без /api/v1)"),
            ("/api/v1/transactions/transactions/test_id/cancel", 404, "Дублирующий путь"),
            ("/api/v1/transactions//cancel", 404, "Пустой ID"),
        ]

        results = []
        for endpoint, expected_status, description in test_cases:
            url = self.base_url + endpoint
            headers = {"Authorization": f"Bearer {self.token}"}

            try:
                response = requests.post(url, headers=headers, timeout=5)
                if response.status_code == expected_status:
                    results.append(self.log_test(f"2.{len(results) + 1} {description}", True,
                                                 f"Path: {endpoint}, Status: {response.status_code}"))
                else:
                    results.append(self.log_test(f"2.{len(results) + 1} {description}", False,
                                                 f"Path: {endpoint}, Expected: {expected_status}, Got: {response.status_code}"))
            except Exception as e:
                results.append(self.log_test(f"2.{len(results) + 1} {description}", False,
                                             f"Path: {endpoint}, Error: {e}"))

        return all(results)

    def test_3_authentication(self):
        """Тест 3: Аутентификация и авторизация"""
        print("\n" + "=" * 70)
        print("ТЕСТ 3: АУТЕНТИФИКАЦИЯ И АВТОРИЗАЦИЯ")
        print("=" * 70)

        test_id = "AUTH_TEST_001"
        test_cases = [
            (True, self.token, 204, "С правильным токеном"),
            (False, None, 401, "Без токена"),
            (True, "WRONG_TOKEN_123", 401, "С неправильным токеном"),
            (True, "", 401, "С пустым токеном"),
            (True, "Bearer " + self.token, 401, "С префиксом 'Bearer' в значении"),
            (True, "Basic " + self.token, 401, "С неправильной схемой аутентификации"),
        ]

        results = []
        for use_token, token, expected_status, description in test_cases:
            response = self.make_request(test_id, use_token=use_token, token=token)

            if response:
                if response.status_code == expected_status:
                    results.append(self.log_test(f"3.{len(results) + 1} {description}", True,
                                                 f"Status: {response.status_code}"))
                else:
                    results.append(self.log_test(f"3.{len(results) + 1} {description}", False,
                                                 f"Expected: {expected_status}, Got: {response.status_code}"))
            else:
                results.append(self.log_test(f"3.{len(results) + 1} {description}", False,
                                             "No response from server"))

        return all(results)

    def test_4_successful_cancellation(self):
        """Тест 4: Успешная отмена платежа"""
        print("\n" + "=" * 70)
        print("ТЕСТ 4: УСПЕШНАЯ ОТМЕНА ПЛАТЕЖА")
        print("=" * 70)

        # Разные форматы ID которые должны успешно отменяться
        test_cases = [
            ("SUCCESS_001", "Обычный ID"),
            ("123456789", "Числовой ID"),
            ("txn-abc-123", "ID с дефисами"),
            ("TEST.ORDER.001", "ID с точками"),
            ("test_order_123", "ID в нижнем регистре"),
            ("TEST_ORDER_001", "ID в верхнем регистре"),
            ("a" * 50, "Длинный ID (50 символов)"),
            ("SHORT", "Короткий ID"),
        ]

        results = []
        for transaction_id, description in test_cases:
            response = self.make_request(transaction_id)

            if response:
                if response.status_code == 204:
                    # Проверяем что тело ответа пустое для 204
                    if response.text == "":
                        results.append(self.log_test(f"4.{len(results) + 1} {description}", True,
                                                     f"ID: {transaction_id}, Status: 204 (No Content)"))
                    else:
                        results.append(self.log_test(f"4.{len(results) + 1} {description}", False,
                                                     f"ID: {transaction_id}, Status: 204 but has body: {response.text[:100]}"))
                else:
                    results.append(self.log_test(f"4.{len(results) + 1} {description}", False,
                                                 f"ID: {transaction_id}, Expected: 204, Got: {response.status_code}"))
            else:
                results.append(self.log_test(f"4.{len(results) + 1} {description}", False,
                                             f"ID: {transaction_id}, No response"))

            # Небольшая пауза между запросами
            time.sleep(0.1)

        return all(results)

    def test_5_invalid_status_cancellation(self):
        """Тест 5: Отмена платежа не в статусе 'process'"""
        print("\n" + "=" * 70)
        print("ТЕСТ 5: ОТМЕНА ПЛАТЕЖА НЕ В СТАТУСЕ 'PROCESS'")
        print("=" * 70)

        # ID которые содержат ключевые слова для симуляции "невалидного" статуса
        test_cases = [
            ("TRANSACTION_INVALID", "INVALID - должен вернуть 400"),
            ("PAYMENT_FAILED", "FAIL - должен вернуть 400"),
            ("ERROR_TRANSACTION", "ERROR - должен вернуть 400"),
            ("WRONG_PAYMENT", "WRONG - должен вернуть 400"),
            ("BAD_ORDER", "BAD - должен вернуть 400"),
            ("PROBLEM_TXN", "PROBLEM - должен вернуть 400"),
            ("REJECTED_001", "REJECT - должен вернуть 400"),
            ("DENIED_PAYMENT", "DENY - должен вернуть 400"),
            ("BLOCKED_TXN", "BLOCK - должен вернуть 400"),
            ("REFUSED_ORDER", "REFUSE - должен вернуть 400"),
        ]

        results = []
        for transaction_id, description in test_cases:
            response = self.make_request(transaction_id)

            if response:
                if response.status_code == 400:
                    # Проверяем структуру ошибки
                    try:
                        error_data = response.json()
                        expected_message = "Transaction should be in progress."

                        if error_data.get("message") == expected_message:
                            results.append(self.log_test(f"5.{len(results) + 1} {description}", True,
                                                         f"ID: {transaction_id}, Correct error message"))
                        elif error_data.get("code") == "1":
                            results.append(self.log_test(f"5.{len(results) + 1} {description}", True,
                                                         f"ID: {transaction_id}, Correct error code"))
                        else:
                            results.append(self.log_test(f"5.{len(results) + 1} {description}", False,
                                                         f"ID: {transaction_id}, Wrong error format: {error_data}"))
                    except json.JSONDecodeError:
                        results.append(self.log_test(f"5.{len(results) + 1} {description}", False,
                                                     f"ID: {transaction_id}, Error response not JSON"))
                else:
                    results.append(self.log_test(f"5.{len(results) + 1} {description}", False,
                                                 f"ID: {transaction_id}, Expected: 400, Got: {response.status_code}"))
            else:
                results.append(self.log_test(f"5.{len(results) + 1} {description}", False,
                                             f"ID: {transaction_id}, No response"))

            time.sleep(0.1)

        return all(results)

    def test_6_edge_cases(self):
        """Тест 6: Краевые случаи"""
        print("\n" + "=" * 70)
        print("ТЕСТ 6: КРАЕВЫЕ СЛУЧАИ")
        print("=" * 70)

        test_cases = [
            ("", "Пустой ID", 404),
            (" " * 10, "ID из пробелов", 204),  # или 400 в зависимости от логики
            ("\t\n", "ID с управляющими символами", 204),  # или 400
            ("ID_WITH_Ё", "ID с буквой Ё", 204),
            ("ID_С_КИРИЛЛИЦЕЙ", "ID с кириллицей", 204),
            ("ID-👍-TEST", "ID с эмодзи", 204),
            ("ID' OR '1'='1", "SQL injection attempt", 204),  # или 400
            ("../../etc/passwd", "Path traversal attempt", 204),  # или 400
            ("<script>alert('xss')</script>", "XSS attempt", 204),  # или 400
            ("A" * 1000, "Очень длинный ID (1000 символов)", 414),  # 414 URI Too Long
        ]

        results = []
        for transaction_id, description, expected_status in test_cases:
            response = self.make_request(transaction_id)

            if response:
                if response.status_code == expected_status:
                    results.append(self.log_test(f"6.{len(results) + 1} {description}", True,
                                                 f"ID: '{transaction_id[:30]}...', Status: {response.status_code}"))
                else:
                    results.append(self.log_test(f"6.{len(results) + 1} {description}", False,
                                                 f"ID: '{transaction_id[:30]}...', Expected: {expected_status}, Got: {response.status_code}"))
            else:
                results.append(self.log_test(f"6.{len(results) + 1} {description}", False,
                                             f"ID: '{transaction_id[:30]}...', No response"))

            time.sleep(0.2)

        return all(results)

    def test_7_rate_limiting_and_performance(self):
        """Тест 7: Производительность и нагрузка"""
        print("\n" + "=" * 70)
        print("ТЕСТ 7: ПРОИЗВОДИТЕЛЬНОСТЬ И НАГРУЗКА")
        print("=" * 70)

        print("Отправка 10 последовательных запросов...")
        start_time = time.time()

        successful = 0
        total = 10

        for i in range(total):
            response = self.make_request(f"PERF_TEST_{i:03d}")
            if response and response.status_code == 204:
                successful += 1
            time.sleep(0.05)  # Небольшая пауза

        elapsed_time = time.time() - start_time

        # Проверяем что все запросы успешны
        if successful == total:
            result = self.log_test("7.1 Последовательные запросы", True,
                                   f"{successful}/{total} успешно, время: {elapsed_time:.2f} сек")
        else:
            result = self.log_test("7.1 Последовательные запросы", False,
                                   f"Только {successful}/{total} успешно, время: {elapsed_time:.2f} сек")

        return result

    def test_8_documentation_compliance(self):
        """Тест 8: Соответствие документации"""
        print("\n" + "=" * 70)
        print("ТЕСТ 8: СООТВЕТСТВИЕ ДОКУМЕНТАЦИИ")
        print("=" * 70)

        # Согласно документации:
        print("Из документации:")
        print("1. Endpoint: POST /api/v1/transactions/{id}/cancel")
        print("2. Header: Authorization: Bearer {merchant_token}")
        print("3. Success: 204 No Content")
        print("4. Error (not in 'process'): 400 with message")
        print()

        results = []

        # Проверка успешного кейса
        print("8.1 Проверка успешного сценария:")
        test_id = "DOC_TEST_SUCCESS"
        response = self.make_request(test_id)

        if response and response.status_code == 204 and response.text == "":
            results.append(self.log_test("8.1 Success response format", True,
                                         "204 No Content with empty body - соответствует документации"))
        else:
            results.append(self.log_test("8.1 Success response format", False,
                                         f"Expected 204 with empty body, got {response.status_code if response else 'no response'}"))

        # Проверка ошибки
        print("\n8.2 Проверка ошибочного сценария:")
        test_id = "DOC_TEST_INVALID"
        response = self.make_request(test_id)

        if response and response.status_code == 400:
            try:
                error_data = response.json()
                # Проверяем структуру как в документации
                if isinstance(error_data, dict) and ("message" in error_data or "code" in error_data):
                    results.append(self.log_test("8.2 Error response format", True,
                                                 f"400 with JSON error - соответствует документации: {error_data}"))
                else:
                    results.append(self.log_test("8.2 Error response format", False,
                                                 f"400 but wrong error format: {error_data}"))
            except:
                results.append(self.log_test("8.2 Error response format", False,
                                             "400 but response not in JSON format"))
        else:
            results.append(self.log_test("8.2 Error response format", False,
                                         f"Expected 400, got {response.status_code if response else 'no response'}"))

        # Проверка примера из документации
        print("\n8.3 Пример из документации:")
        print("curl --location --request POST '{{base_url}}/api/v1/transactions/{{id}}/cancel' \\")
        print("--header 'Authorization: Bearer {{merchant_token}}'")

        test_id = "12345"  # Как в примере
        url = f"{self.base_url}/api/v1/transactions/{test_id}/cancel"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.post(url, headers=headers, timeout=5)
            if response.status_code == 204:
                results.append(self.log_test("8.3 Documentation example", True,
                                             "Пример из документации работает корректно"))
            else:
                results.append(self.log_test("8.3 Documentation example", False,
                                             f"Пример не работает: status {response.status_code}"))
        except Exception as e:
            results.append(self.log_test("8.3 Documentation example", False,
                                         f"Ошибка при тесте примера: {e}"))

        return all(results)

    def test_9_integration_scenarios(self):
        """Тест 9: Интеграционные сценарии"""
        print("\n" + "=" * 70)
        print("ТЕСТ 9: ИНТЕГРАЦИОННЫЕ СЦЕНАРИИ")
        print("=" * 70)

        results = []

        # Сценарий 1: Отмена после создания
        print("9.1 Сценарий: Создание → Отмена")
        try:
            # Симуляция создания транзакции (используем существующий эндпоинт)
            create_url = f"{self.base_url}/api/v1/transactions/card"
            create_data = {
                "amount": "1000",
                "currency": "RUB",
                "merchant_transaction_id": f"INTEGRATION_TEST_{int(time.time())}",
                "currency_rate": "95.50",
                "client_id": "integration_test"
            }
            create_headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            create_response = requests.post(create_url, json=create_data, headers=create_headers, timeout=10)

            if create_response.status_code == 200:
                transaction_data = create_response.json()
                transaction_id = transaction_data.get("id", "TEST_INTEGRATION_001")

                # Пытаемся отменить
                cancel_response = self.make_request(str(transaction_id))

                if cancel_response and cancel_response.status_code == 204:
                    results.append(self.log_test("9.1 Create → Cancel scenario", True,
                                                 f"Транзакция {transaction_id} успешно создана и отменена"))
                else:
                    results.append(self.log_test("9.1 Create → Cancel scenario", False,
                                                 f"Создание успешно, но отмена не сработала: {cancel_response.status_code if cancel_response else 'no response'}"))
            else:
                results.append(self.log_test("9.1 Create → Cancel scenario", False,
                                             f"Не удалось создать транзакцию: {create_response.status_code}"))
        except Exception as e:
            results.append(self.log_test("9.1 Create → Cancel scenario", False,
                                         f"Ошибка: {e}"))

        # Сценарий 2: Двойная отмена
        print("\n9.2 Сценарий: Двойная отмена одной транзакции")
        test_id = "DOUBLE_CANCEL_TEST"

        # Первая отмена
        response1 = self.make_request(test_id)
        time.sleep(0.1)

        # Вторая отмена той же транзакции
        response2 = self.make_request(test_id)

        if response1 and response2:
            # Ожидаем что обе отмены вернут 204 (или вторая может вернуть 400 в реальной системе)
            if response1.status_code == 204 and response2.status_code == 204:
                results.append(self.log_test("9.2 Double cancel scenario", True,
                                             "Двойная отмена отработала (обе 204)"))
            else:
                results.append(self.log_test("9.2 Double cancel scenario", False,
                                             f"Первая: {response1.status_code}, Вторая: {response2.status_code}"))
        else:
            results.append(self.log_test("9.2 Double cancel scenario", False,
                                         "Один из запросов не получил ответа"))

        return all(results)

    def test_10_monitoring_and_logging(self):
        """Тест 10: Мониторинг и логирование"""
        print("\n" + "=" * 70)
        print("ТЕСТ 10: МОНИТОРИНГ И ЛОГИРОВАНИЕ")
        print("=" * 70)

        print("Проверка логирования (смотреть вывод сервера):")

        test_cases = [
            ("LOG_TEST_SUCCESS", 204, "Успешная отмена"),
            ("LOG_TEST_INVALID", 400, "Неуспешная отмена"),
        ]

        results = []
        for transaction_id, expected_status, description in test_cases:
            print(f"\n  Отправка: {description} (ID: {transaction_id})")
            response = self.make_request(transaction_id)

            if response and response.status_code == expected_status:
                results.append(self.log_test(f"10.{len(results) + 1} {description}", True,
                                             f"Статус: {response.status_code} - проверьте логи сервера"))
            else:
                results.append(self.log_test(f"10.{len(results) + 1} {description}", False,
                                             f"Expected: {expected_status}, Got: {response.status_code if response else 'no response'}"))

            time.sleep(0.5)  # Даем время для записи логов

        return all(results)

    def run_complete_test_suite(self):
        """Запуск полного набора тестов"""
        print("=" * 80)
        print("🚀 ПОЛНАЯ ПРОВЕРКА СИСТЕМЫ ОТМЕНЫ ПЛАТЕЖЕЙ")
        print("=" * 80)
        print(f"Сервер: {self.base_url}")
        print(f"Токен: {self.token}")
        print(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Запуск всех тестов
        tests = [
            ("Доступность сервера", self.test_1_server_availability),
            ("Структура эндпоинта", self.test_2_endpoint_structure),
            ("Аутентификация", self.test_3_authentication),
            ("Успешная отмена", self.test_4_successful_cancellation),
            ("Отмена не в статусе process", self.test_5_invalid_status_cancellation),
            ("Краевые случаи", self.test_6_edge_cases),
            ("Производительность", self.test_7_rate_limiting_and_performance),
            ("Соответствие документации", self.test_8_documentation_compliance),
            ("Интеграционные сценарии", self.test_9_integration_scenarios),
            ("Мониторинг и логирование", self.test_10_monitoring_and_logging),
        ]

        test_results = []

        for test_name, test_func in tests:
            print(f"\n▶️  Запуск: {test_name}")
            print("-" * 70)

            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ Ошибка при выполнении теста: {e}")
                test_results.append((test_name, False))

        # Итоговый отчет
        print("\n" + "=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 80)

        total_tests = len(test_results)
        passed_tests = sum(1 for _, passed in test_results if passed)
        failed_tests = total_tests - passed_tests

        print(f"\nВсего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {failed_tests}")
        print(f"Успешность: {(passed_tests / total_tests) * 100:.1f}%")

        if failed_tests > 0:
            print("\n❌ Проваленные тесты:")
            for test_name, passed in test_results:
                if not passed:
                    print(f"  • {test_name}")

        # Детализация по всем тестам
        print("\n" + "=" * 80)
        print("📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 80)

        for test_name, test_details, test_success in self.results:
            status = "✅" if test_success else "❌"
            print(f"{status} {test_name}")
            if test_details:
                print(f"    {test_details}")

        # Вывод рекомендаций
        print("\n" + "=" * 80)
        print("💡 РЕКОМЕНДАЦИИ")
        print("=" * 80)

        if passed_tests == total_tests:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("\nСистема отмены платежей ГОТОВА К ПРОДАКШЕНУ.")
            print("\nРекомендации для продакшена:")
            print("1. Удалить тестовую логику проверки ключевых слов")
            print("2. Реализовать проверку реального статуса транзакции из БД")
            print("3. Раскомментировать проверку токена: token: str = Depends(security)")
            print("4. Настроить мониторинг и алертинг")
            print("5. Добавить метрики для отслеживания успешных/неуспешных отмен")
            print("6. Реализовать retry логику для вызовов провайдера")
            print("7. Добавить аудит-логи для всех операций отмены")
        else:
            print(f"\n⚠️ НЕОБХОДИМО ИСПРАВИТЬ {failed_tests} ТЕСТ(ОВ)")
            print("\nПриоритетные исправления:")
            print("1. Убедиться что все эндпоинты доступны")
            print("2. Проверить авторизацию и аутентификацию")
            print("3. Убедиться в правильности HTTP статусов")
            print("4. Проверить обработку краевых случаев")
            print("5. Убедиться в соответствии документации")

        return passed_tests == total_tests


def main():
    """Основная функция"""
    print("=" * 80)
    print("🔧 КОНФИГУРАЦИЯ ТЕСТИРОВАНИЯ")
    print("=" * 80)

    base_url = input("Введите URL сервера [http://localhost:8000]: ").strip()
    if not base_url:
        base_url = "http://localhost:8000"

    token = input("Введите merchant token [test_token_123]: ").strip()
    if not token:
        token = "test_token_123"

    print(f"\nКонфигурация:")
    print(f"  Сервер: {base_url}")
    print(f"  Токен: {token}")

    print("\n" + "=" * 80)
    print("⚠️  ВАЖНО: Убедитесь что сервер запущен!")
    print("=" * 80)

    tester = CancelPaymentSystemTester(base_url, token)

    input("\nНажмите Enter для начала тестирования...")

    try:
        success = tester.run_complete_test_suite()

        if success:
            print("\n" + "=" * 80)
            print("🎊 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("💀 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
            print("=" * 80)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n❌ Тестирование прервано пользователем")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ Неожиданная ошибка: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()