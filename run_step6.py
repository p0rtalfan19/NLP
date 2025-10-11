#!/usr/bin/env python3
"""
Этап 6: Веб-интерфейс для интерактивного анализа
"""
import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("ЭТАП 6: ВЕБ-ИНТЕРФЕЙС ДЛЯ ИНТЕРАКТИВНОГО АНАЛИЗА")
    print("=" * 60)
    
    # Проверяем наличие файла веб-интерфейса
    web_interface_file = "C:/Users/GomonovDP/PycharmProjects/pythonProject/NLP/web_interface.py"
    if not os.path.exists(web_interface_file):
        print(f"❌ Файл {web_interface_file} не найден!")
        return
    
    print("🌐 Запуск веб-интерфейса...")
    print("🌐 Запуск веб-интерфейса...")
    print("📝 Веб-интерфейс предоставляет:")
    print("   • Загрузку данных (примеры, Коммерсантъ, файлы)")
    print("   • Настройку предобработки")
    print("   • Анализ токенизации")
    print("   • Обучение подсловных моделей")
    print("   • Визуализацию результатов")
    print("   • Экспорт отчетов")
    
    print(f"\n🚀 Запускаем Streamlit...")
    print(f"📱 Откройте браузер по адресу: http://localhost:8501")
    print(f"⏹️ Для остановки нажмите Ctrl+C")
    
    try:
        # Запуск Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", web_interface_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска Streamlit: {e}")
        print("💡 Убедитесь, что Streamlit установлен: pip install streamlit")
    except KeyboardInterrupt:
        print(f"\n⏹️ Веб-интерфейс остановлен")
    
    print("\n🎉 Этап 6 завершен!")

if __name__ == "__main__":
    main()

