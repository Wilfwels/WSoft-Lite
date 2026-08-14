import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Label, filedialog
import hashlib
import os
import sys
from datetime import datetime
from configuracion import abrir_configuracion
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
from openpyxl import Workbook
from PIL import Image, ImageTk
from utils.barra_reportes import barra_reportes
from reportes_utils import generar_reporte_pdf, crear_botones_reporte
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportes.utilidades import *
