from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import disk_offload
import torch


class AnswerGenerator:

    def __init__(self, model = "DiscoResearch/Llama3-DiscoLeo-Instruct-8B-v0.1"):

        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype=torch.float16, 
            low_cpu_mem_usage = True).cpu() 

        disk_offload(model=model, offload_dir="offload")

        self.tokenizer = AutoTokenizer.from_pretrained(model)

        
    def generate_answer(self, query: str, contexts = []):

        messages = [
            {"role": "system", "content": "Beantworte die Fragen anhand des gegebenen Kontexts."},
            {"role": "user", "content": query}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt")

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return response