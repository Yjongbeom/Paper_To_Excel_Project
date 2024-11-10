from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

os.environ['HF_HOME'] = '/home/swsong/Guchung/.cache/huggingface'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B'
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
model.eval()

class AIColumnsView(APIView):
    """텍스트에서 열 제목을 추출하여 반환하는 API"""
    def post(self, request):
        try:
            text = request.data.get('text')

            messages = [
                {"role": "system", "content": (
                    "You are a skilled data analyst. Extract and return the most relevant column names from the provided text. "
                    "Ensure that the column names are concise, relevant, and free of typographical errors. "
                    "The column names should be in Korean and should match the data context exactly."
                    "Don't leave a note, just show a response"
                )},
                {"role": "user", "content": f"{text}"}
            ]

            input_ids = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(model.device)

            terminators = [
                tokenizer.eos_token_id,
                tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]

            outputs = model.generate(
                input_ids,
                max_new_tokens=256,
                eos_token_id=terminators,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
                repetition_penalty=1.1
            )

            response_text = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

            return Response({'response': response_text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIResponseView(APIView):
    """텍스트와 열 정보를 기반으로 표 데이터를 추출하는 API"""
    def post(self, request):
        try:
            text = request.data.get('text')
            columns = request.data.get('columns')

            messages = [
                {"role": "system", "content": (
                    "You are an AI that extracts structured information from text. "
                    "Please convert the following information into a well-formatted table with rows and columns aligned correctly. "
                    "Ensure that all columns and rows are represented correctly. "
                    "and handle cases where multiple spaces or irregular spacing occurs by treating it as a single space. "
                    "If multiple pieces of information, such as bank name and account number, are in one cell, separate them into different columns. "
                    "Combine similar or identical column headers into one column, and fill in missing data with '-'. "
                    "Do not leave notes in the response, just return the formatted table."
                    )},
                {"role": "user", "content": (
                        "Here is the text with information that needs to be converted into a table. "
                        "The table should have the following columns: " + ', '.join(columns) + ".\n\n" + text
                )}
            ]

            input_ids = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(model.device)

            terminators = [
                tokenizer.eos_token_id,
                tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]

            outputs = model.generate(
                input_ids,
                max_new_tokens=256,
                eos_token_id=terminators,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
                repetition_penalty=1.1
            )

            response_text = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

            return Response({'response': response_text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

