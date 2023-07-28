import os
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox
from pytube import Playlist
from concurrent.futures import ThreadPoolExecutor

def get_playlist_songs(playlist_url):
    # Получаем объект Playlist
    playlist = Playlist(playlist_url)
    
    # Получаем название плейлиста
    response = requests.get(playlist_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    playlist_title = soup.find('title').text.split(' - YouTube')[0].strip()

    # Загружаем информацию о видео многопоточно
    song_titles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(get_video_title, video) for video in playlist.videos]
        for future in futures:
            title = future.result()
            song_titles.append(title)

    return playlist_title, song_titles

def get_video_title(video):
    return video.title

def save_to_txt(playlist_title, song_titles, file_path):
    file_name = os.path.join(file_path, f"{playlist_title}.txt")
    with open(file_name, 'w', encoding='utf-8') as file:
        for title in song_titles:
            file.write(f"{title}\n")
    return file_name

def print_songs(playlist_title, song_titles, playlist_text):
    playlist_text.delete(1.0, tk.END)  # Очищаем виджет Text
    playlist_text.insert(tk.END, f"Название плейлиста: {playlist_title}\nСписок песен:\n")
    for title in song_titles:
        playlist_text.insert(tk.END, f"{title}\n")

def on_get_list_button_click(playlist_url, playlist_text):
    if not playlist_url.startswith("https://www.youtube.com/playlist?"):
        messagebox.showerror("Ошибка!", "Пожалуйста, введите корректную ссылку на плейлист YouTube.")
        return

    try:
        playlist_title, song_titles = get_playlist_songs(playlist_url)
        print_songs(playlist_title, song_titles, playlist_text)
        file_name = save_to_txt(playlist_title, song_titles, os.getcwd())
        messagebox.showinfo("Успех!", f"Список песен сохранен в файле:\n{file_name}")
    except requests.exceptions.HTTPError:
        messagebox.showerror("Ошибка!", "Не удалось получить данные. Проверьте ссылку на плейлист.")
    except Exception as e:
        messagebox.showerror("Ошибка!", f"Не удалось получить список песен.\nОшибка: {str(e)}")

def create_gui():
    root = tk.Tk()
    root.title("Парсер YouTube плейлиста")

    url_label = tk.Label(root, text="Ссылка на плейлист YouTube:")
    url_label.pack()

    url_entry = tk.Entry(root, width=50)
    url_entry.pack()

    get_list_button = tk.Button(root, text="Получить список песен", command=lambda: on_get_list_button_click(url_entry.get(), playlist_text))
    get_list_button.pack()

    playlist_text = tk.Text(root, width=80, height=20)
    playlist_text.pack()

    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
